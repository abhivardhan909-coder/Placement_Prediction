# Placement Prediction Runbook

Run commands from the repository root in PowerShell.

## Initial setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Keep the raw source at `data/raw/Placement_Data_Full_Class.csv`. The expected target is `status`, with values `Placed` and `Not Placed`. `config.yaml` is the authoritative source for data paths and target encoding.

## Train, evaluate, and deploy

```powershell
python .\src\mlops_pipeline\placement_prediction_pipeline.py
```

The script validates and preprocesses the dataset, trains and registers a model in the local MLflow store, evaluates the candidate, applies the quality gate, and promotes/deploys only when the lifecycle stage approves the candidate. A current dataset is sufficient; ingestion of an additional batch is optional.

For optional batch ingestion, place a schema-compatible CSV at `data/raw/new_placement_data.csv`, with unique `sl_no` values that are not already in the current dataset, then rerun the pipeline.

## API checks

The deployment bundle must exist under `deployment/`. Run the app:

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Use `/health`, `/metadata`, `/predict`, or `/predict/batch`. Run local tests with `python -m pytest .\tests\test_api.py .\tests\test_performance.py`. The container comparison test requires the container to be serving on `localhost:8000`.

## Docker and Kubernetes

```powershell
docker build -t placement-prediction-api:latest .
kubectl get nodes
python .\deployment\deploy_production.py
kubectl rollout status deployment/placement-api
kubectl get pods -l app=placement-api
kubectl get service placement-api-service
```

Docker Desktop Kubernetes shares its local image cache. For a remote cluster, push the image to a registry and update `k8s/deployment.yaml`.

## Common failures

- **Dataset missing or invalid:** confirm the filename and exact columns in `data/raw/Placement_Data_Full_Class.csv`; inspect `artifacts/baseline_validation.csv`. Successful validation rewrites this report with the current placement schema.
- **Missing model files:** rerun the MLOps pipeline to prepare `deployment/model.pkl`, `deployment/preprocessor.pkl`, and `deployment/model_metadata.json`.
- **Registry unavailable:** keep the configured local `sqlite:///mlflow.db` tracking URI consistent between the training and deployment stages.
- **Kubernetes image pull failure:** verify Docker Desktop Kubernetes is the active context and that `placement-prediction-api:latest` is locally available.
- **API returns 503 at startup:** verify the deployment bundle is complete and rebuild the image after regenerating it.

Generated MLflow state, logs, processed arrays, and prediction outputs are local runtime data and should not be committed.
