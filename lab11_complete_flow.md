# Placement Prediction: Docker and Kubernetes

This project serves the Placement Prediction model through FastAPI. The
canonical setup, API examples, Docker commands, and Kubernetes deployment
instructions are maintained in the [README](README.md) and
[runbook](docs/RUNBOOK.md).

## Quick deployment

From the repository root in PowerShell:

```powershell
python .\src\mlops_pipeline\placement_prediction_pipeline.py
docker build -t placement-prediction-api:latest .
python .\deployment\deploy_production.py
kubectl rollout status deployment/placement-api
kubectl port-forward service/placement-api-service 8000:8000
```

In another terminal, confirm `http://127.0.0.1:8000/health` responds before
sending placement records to `POST /predict`.

The current Kubernetes resources use the local Docker Desktop image and
the `placement-api` deployment. Remote clusters require publishing the
image to an accessible container registry and updating the deployment
manifest.
