# Project Dependency Analysis

## Scope and method

This was a static, read-only inspection of source, configuration, model artifacts, and requirement files. No packages were installed, no model artifact was deserialized, no model was trained, no pipeline was run, and no deployment was performed.

## Missing model dependencies

| Missing file | Expected size | Executable dependency status | Effect |
|---|---:|---|---|
| `models/churn_full_pipeline.pkl` | 5,780,411 bytes | No executable source or configuration reference found. | Not a current runtime blocker based on the restored codebase. |
| `models/churn_model.pkl` | 15,030,889 bytes | Referenced by `config.yaml` as `paths.model`. | Blocks the local model-evaluation stage and the Lab 9 missing-model recovery exercise until restored or legitimately regenerated. It is not the API serving model. |

## Files that reference the missing models

### `models/churn_full_pipeline.pkl`

No Python, YAML, JSON, workflow, or deployment code references this filename. It occurs only in the package reconstruction documentation (`FILE_PLACEMENT_MAP.csv`, `PROJECT_STRUCTURE.txt`, and `PROJECT_SETUP_REPORT.md`).

### `models/churn_model.pkl`

- `config.yaml` directly configures `paths.model: models/churn_model.pkl`.
- `src/mlops_pipeline/05_train_registry.py` uses that configuration as the destination for the locally trained candidate model.
- `src/mlops_pipeline/06_model_evaluation.py` loads that configured path and exits unsuccessfully if it is absent.
- `src/mlops_pipeline/10_failure_injection.py` uses the same path for its missing-model/recovery scenario and would report that scenario as not tested while it is absent.
- `docs/LAB9_FAILURE_HANDLING_REPORT.md` records the historical missing-model scenario; it is documentation, not runtime code.

## API and prediction impact

The FastAPI application does **not** load either missing `models/` file.

`api/main.py` loads a `ModelLoader` during the FastAPI lifespan startup. `api/model_loader.py` requires this separate deployment bundle:

| Required API startup file | Status |
|---|---|
| `config.yaml` | Present |
| `deployment/model.pkl` | Present (5,808,041 bytes) |
| `deployment/preprocessor.pkl` | Present (7,551 bytes) |
| `deployment/model_metadata.json` | Present |

Therefore, the API can start and its single/batch prediction routes can use `deployment/model.pkl` plus `deployment/preprocessor.pkl`, subject to the required Python environment being installed and pickle-version compatibility. The metadata identifies this as `Telco_Churn_Production_Model`, version `1`, sourced from MLflow run `e6b24fcde8574a95a7bc1ce6da74b0dc`.

The pipeline inference demo (`src/mlops_pipeline/09_inference.py`) also does not use either missing local artifact: it loads the Production model from MLflow and requires the existing `models/preprocessor.pkl` and `data/raw/churn.csv`.

## Available model artifacts and equivalents

The project has these relevant available artifacts:

- `deployment/model.pkl` and its matching deployment preprocessor, used only for serving.
- `models/random_forest_model.pkl` and `models/random_forest_baseline.pkl`, which are byte-identical to each other (same 5,764,969-byte SHA-256 digest).
- `models/churn_xgboost_pipeline.pkl`.
- `models/retrained_model_v2.pkl` and `models/retrained_preprocessor_v2.pkl`.
- Baseline artifacts, `models/preprocessor.pkl`, `models/ohe.pkl`, `models/scaler.pkl`, and `models/churn_decision_threshold.pkl`.

None can be proven equivalent to either missing model because the missing files are unavailable for metadata or hash comparison. In particular, `deployment/model.pkl` is a distinct artifact and should not be substituted for `models/churn_model.pkl` without an explicit compatibility and provenance decision.

## Required Python packages

`requirements.txt` contains 176 active, exactly pinned packages: the full development/pipeline environment. Directly imported project dependencies include `numpy`, `pandas`, `scikit-learn`, `joblib`, `PyYAML`, `mlflow`, `pandera`, `matplotlib`, `fastapi`, `pydantic`, `uvicorn`, and `docker`.

`requirements-api.txt` defines the lean serving set:

```text
fastapi==0.141.1
uvicorn==0.52.4
pydantic==2.13.4
numpy==2.4.6
pandas==2.3.3
scikit-learn==1.9.0
joblib==1.5.3
PyYAML==6.0.3
```

The Dockerfile uses `python:3.11-slim` and installs this API requirements file.

## Potential compatibility and runtime problems

1. **Python version:** Python 3.11 is the project’s declared target and container runtime. This is required in practice: `scikit-learn==1.9.0` requires Python 3.11 or newer. Python 3.10 or older will not satisfy the pinned machine-learning stack.
2. **Serialized model compatibility:** `joblib`/scikit-learn model files are version-sensitive. The repository does not preserve the training-time Python, scikit-learn, NumPy, or joblib versions for `deployment/model.pkl`; loading it under the pinned environment is unverified and may issue an incompatibility warning or fail.
3. **MLflow state is absent:** the handout intentionally excludes the local MLflow store/database and artifacts. Stages using `MlflowClient`, registry URIs, or `models:/.../Production` need access to the original compatible tracking store or a configured replacement. This affects stages 05, 08–11, 12, and several utility scripts.
4. **Generated outputs/logs are absent:** `outputs/` and `logs/inference/inference_log.jsonl` are not present. Monitoring, drift-analysis, request-history, and retraining-update scripts require particular generated reports/logs before they can run. These are runtime products, not missing source files.
5. **Tests lack a declared test runner:** `tests/test_api.py` imports `pytest`, but neither requirements file explicitly declares `pytest`. API tests also enter the FastAPI lifespan and therefore require the deployment bundle to deserialize successfully.
6. **Unrelated source defect:** `src/validate_outputs.py` has a syntax error at `report = {4`, so that legacy script cannot run until corrected. The active pipeline’s separate `src/mlops_pipeline/04_validate_outputs.py` is the stage invoked by the orchestrator.
7. **Pin resolution remains untested:** requirements are a large, exact lock-style list without hashes or a documented resolver result. Their installation/resolution was deliberately not attempted. The separate API list is the appropriate minimum environment for serving; the full list is required for MLflow/pipeline work.

## Other missing restored package entries

The setup report also lists two zero-byte entries absent from the package: `api/__init__.py` and an anomalous root path named `}`. The first is not required for Python namespace-package imports in this layout; the latter has no code reference.

## Recommended next steps

1. Retain the existing deployment bundle unchanged and use it as the only API-serving artifact unless its provenance is independently verified.
2. Obtain the two missing model files from the original project backup or the MLflow artifact store, preserving their original versions and checksums. Do not rename or substitute another artifact as a replacement.
3. Before any model load, create a clean Python 3.11 environment and resolve the pinned dependencies; validate model deserialization and API tests separately from the training pipeline.
4. Configure or restore the MLflow tracking URI/store before attempting registry, lifecycle, inference-demo, recovery, or deployment-preparation stages.
5. Treat `src/validate_outputs.py` and the undeclared `pytest` test dependency as follow-up maintenance work. Do not change them as part of model restoration without separate approval.
