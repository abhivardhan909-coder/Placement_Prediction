# Placement Prediction

An end-to-end machine-learning project that predicts whether a student is placed using the dataset in `data/raw/Placement_Data_Full_Class.csv`. The MLOps workflow validates the data, prepares a repeatable train/test split, trains and evaluates a classifier, tracks the run with MLflow, and serves the registered model through FastAPI, Docker, and Kubernetes.

## Dataset and labels

The raw dataset has 215 records and 14 columns. `status` is the target (`Placed` or `Not Placed`), and `sl_no` is an identifier that is excluded from model features. The target is encoded as `Placed = 1` and `Not Placed = 0`. Academic scores are constrained to the 0–100 range; categorical values are checked against the dataset schema.

Incoming placement records can optionally be placed at `data/raw/new_placement_data.csv`. The ingestion stage validates their schema and unique `sl_no` values before appending them. The canonical data path, split, label mapping, model, and MLflow registry settings are in [config.yaml](./config.yaml).

## Setup

Use Python 3.11 and run commands from the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For API-only serving, install `requirements-api.txt` instead. Docker Desktop and Docker Desktop Kubernetes are required for container and cluster deployment. `kubectl` must use the intended Kubernetes context.

## Run the ML pipeline

```powershell
python .\src\mlops_pipeline\placement_prediction_pipeline.py
```

The pipeline continues with the current dataset when there is no incoming batch. It writes MLflow data to the local ignored `mlflow.db`, and regenerates processed splits, reports, and deployment artifacts.

Main generated outputs:

- `data/processed/`: fixed split IDs, transformed features, and dataset metadata
- `models/`: fitted preprocessing and model artifacts
- `artifacts/` and `reports/`: validation, evaluation, quality-gate, lifecycle, and deployment reports
- `outputs/placement_predictions.csv`: sample predictions
- `logs/placement_prediction_pipeline_run_log.json`: stage-by-stage run status

Run the API tests after the deployment bundle has been prepared:

```powershell
python -m pytest .\tests\test_api.py .\tests\test_performance.py
```

## Run the API locally

Start the service from the repository root after a deployment bundle exists:

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

`GET /health` checks service health; `GET /metadata` reports the loaded model. Send a placement request to `POST /predict`:

```powershell
$body = @{
  gender = "M"; ssc_p = 67.0; ssc_b = "Others"; hsc_p = 91.0
  hsc_b = "Others"; hsc_s = "Commerce"; degree_p = 58.0
  degree_t = "Sci&Tech"; workex = "No"; etest_p = 55.0
  specialisation = "Mkt&HR"; mba_p = 58.8
} | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/predict -Method Post `
  -ContentType "application/json" -Body $body
```

The response contains the binary prediction, `predicted_status`, and `placement_probability`. `/predict/batch` accepts a non-empty `customers` array with the same fields.

## Docker

Build and run the image:

```powershell
docker build -t placement-prediction-api:latest .
docker run --rm -p 8000:8000 placement-prediction-api:latest
```

In another terminal, check `http://127.0.0.1:8000/health` and run the sample request above. To compare local and container predictions, keep the container running on port 8000 and run:

```powershell
python -m pytest .\tests\test_local_vs_container.py
```

## Kubernetes

The manifests target Docker Desktop Kubernetes and use the locally built image:

```powershell
kubectl get nodes
python .\deployment\deploy_production.py
kubectl get deployment placement-api
kubectl get pods -l app=placement-api
kubectl get service placement-api-service
```

The service is exposed on NodePort `30080`. You can also forward it to localhost:

```powershell
kubectl port-forward service/placement-api-service 8000:8000
```

Check `http://127.0.0.1:8000/health`, then send the sample request. To remove only this project's Kubernetes resources:

```powershell
kubectl delete -f .\k8s\service.yaml
kubectl delete -f .\k8s\deployment.yaml
```

For a remote cluster, publish the image to a registry and update the image in `k8s/deployment.yaml`; a local Docker Desktop image is not available to arbitrary remote nodes.

## GitHub

The intended repository is [abhivardhan909-coder/Placement_Prediction](https://github.com/abhivardhan909-coder/Placement_Prediction). Do not commit credentials, `.env` files, the local MLflow database, virtual environments, or generated predictions/logs. See [docs/RUNBOOK.md](./docs/RUNBOOK.md) for troubleshooting and operational guidance.
