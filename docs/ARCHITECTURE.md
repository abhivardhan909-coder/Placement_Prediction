# Placement Prediction Architecture

```text
data/raw/Placement_Data_Full_Class.csv
              |
              v
   schema validation (status, sl_no, score ranges)
              |
              v
 train/test split -> imputation -> scaling/one-hot encoding
              |
              v
 Random Forest training -> MLflow tracking and registry
              |
              v
 evaluation -> F1 quality gate -> model lifecycle decision
              |
       promoted candidate only
              v
 deployment bundle -> Docker image -> Kubernetes Deployment/Service
              |
              v
 FastAPI /predict and /predict/batch
```

The model predicts `status`: `Placed` is encoded as `1`, and `Not Placed` as `0`. The `sl_no` identifier and target are excluded from model features. One fitted preprocessing pipeline is shared by training and API inference.

The pipeline uses project-root paths, so the orchestrator can run its stage scripts from the repository root. Deployment artifacts are written to `deployment/`; generated splits, reports, logs, and outputs stay in ignored runtime folders. Kubernetes uses the locally built `placement-prediction-api:latest` image for Docker Desktop.
