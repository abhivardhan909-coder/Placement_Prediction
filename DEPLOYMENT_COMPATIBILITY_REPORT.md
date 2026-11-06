# Deployment Artifact Compatibility Report

## Result

**Compatible in the tested environment.** The deployment model and preprocessor loaded successfully through the exact `ModelLoader.load()` path used by the FastAPI application's lifespan startup. No pickle, joblib, scikit-learn, or library compatibility warnings/errors were emitted.

No API server was started. No model files were modified, regenerated, overwritten, or deserialized for prediction.

## Loader behavior inspected

`api/model_loader.py`:

1. Resolves the project root from `api/model_loader.py`.
2. Reads `config.yaml` with `yaml.safe_load()`.
3. Requires `deployment/model.pkl`, `deployment/preprocessor.pkl`, and `deployment/model_metadata.json` to exist.
4. Reads metadata as JSON.
5. Calls `joblib.load()` on `deployment/model.pkl`.
6. Calls `joblib.load()` on `deployment/preprocessor.pkl`.
7. Treats the bundle as ready only when both loaded objects are non-null.

`api/main.py` calls this loader in its FastAPI lifespan startup handler, so this check exercised the same artifact-loading code path without starting Uvicorn or serving requests.

## Deployment metadata

| Field | Value |
|---|---|
| Model name | `Telco_Churn_Production_Model` |
| Model version | `1` |
| Model stage | `Production` |
| MLflow run ID | `e6b24fcde8574a95a7bc1ce6da74b0dc` |
| MLflow model ID | `m-0b44c639cae04d2da060f7b7f01e34d1` |
| Preprocessor source artifact | `preprocessing_pipeline/preprocessor.pkl` |

## Tested environment

| Component | Installed version |
|---|---|
| Python | `3.11.9` (64-bit) |
| NumPy | `2.4.6` |
| Pandas | `2.3.3` |
| Scikit-learn | `1.9.0` |
| Joblib | `1.5.3` |

## Actual load result

| Artifact | Load result | Loaded object | Expected callable methods | Observed feature count |
|---|---|---|---|---:|
| `deployment/model.pkl` | Success | `sklearn.ensemble._forest.RandomForestClassifier` | `predict`: yes; `predict_proba`: yes | 30 |
| `deployment/preprocessor.pkl` | Success | `sklearn.compose._column_transformer.ColumnTransformer` | `transform`: yes | 19 |

`ModelLoader.is_ready()` returned `True` after loading both artifacts.

The API’s prediction handlers call `preprocessor.transform(...)`, followed by `model.predict(...)` and `model.predict_proba(...)`. All three required callable methods are present. This check intentionally did not submit data or execute a prediction.

## Warnings and errors

None. Standard error was empty with Python warnings enabled (`-W always`). The loader returned process exit code `0`.

## Artifact integrity check

SHA-256 hashes were recorded before and after the load test and were unchanged:

| File | SHA-256 |
|---|---|
| `deployment/model.pkl` | `C91C8B2E13579C6C894046CC345085EF76D88803F0DFABB3130D78AD77DF32CB` |
| `deployment/preprocessor.pkl` | `6A8C04562EBA9E73B24CFF5B30F800D823819268DA2DA7487B3627D7511EE458` |
| `deployment/model_metadata.json` | `F8E883B641B8A79F8D286A707D4502D4A9023ABB63F1F6D8D047DE8449FE4169` |

Bytecode writing was disabled during testing; no `__pycache__` directories or diagnostic Python processes remained after the check.

## Scope limitation

Successful deserialization and method inspection demonstrate compatibility with this installed environment. They do not independently validate prediction correctness, schema compatibility for real requests, model metrics, MLflow registry reachability, container execution, or deployment behavior.
