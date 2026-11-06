# Project Setup Report

## Result

The Customer Churn Prediction project directory structure has been reconstructed from `FILE_PLACEMENT_MAP.csv` and `PROJECT_STRUCTURE.txt`.

- Mapped entries: 146
- Successfully restored: 142
- Files moved into mapped subdirectories: 130
- Destination collisions: 0
- Expected mapped directories verified: 18
- Existing file-size mismatches (excluding the intentionally re-encoded requirements file): 0

The handout guides (`HOW_TO_USE_THIS_PACKAGE.txt`, `FILE_PLACEMENT_MAP.csv`, and `PROJECT_STRUCTURE.txt`) were retained at the project root for traceability. No files were deleted or overwritten.

## Renamed packaged files resolved

The following packaged-name conventions were restored to their original names and locations:

- `api____init__.py` -> `api/__init__.py` (source missing; see below)
- `deployment__preprocessor.pkl` -> `deployment/preprocessor.pkl`
- `models__preprocessor.pkl` -> `models/preprocessor.pkl`
- `tests____init__.py` -> `tests/__init__.py`

All other available files were placed according to the mapping, including datasets, notebooks, reports, deployment files, workflows, tests, and model artifacts.

## Requirements encoding

`requirements.txt` was UTF-16 LE with a BOM. It was converted to valid UTF-8 without a BOM while preserving its textual dependency content. Its byte size consequently changed from 6,994 to 3,496 bytes.

## Missing mapped files

These entries appear in the placement map but were not present in the supplied package, so they could not be restored:

| Expected path | Packaged name | Expected size | Notes |
|---|---|---:|---|
| `}` | `}` | 0 bytes | Zero-byte, anomalous map/structure entry. |
| `api/__init__.py` | `api____init__.py` | 0 bytes | Zero-byte package marker absent. |
| `models/churn_full_pipeline.pkl` | `churn_full_pipeline.pkl` | 5,780,411 bytes | Model artifact absent. |
| `models/churn_model.pkl` | `churn_model.pkl` | 15,030,889 bytes | Model artifact absent. |

## Verification

All expected mapped directories exist:

` .github/workflows`, `api`, `artifacts`, `data/monitoring/drift`, `data/processed`, `data/raw/archive`, `deployment`, `docs`, `k8s`, `lab11_commands`, `models`, `notebooks`, `pipelines`, `reports`, `src/mlops_pipeline`, and `tests`.

Important preserved files include the raw and processed datasets, both notebooks, available `.pkl` model artifacts, reports, API/deployment sources, pipeline sources, tests, and GitHub workflow definitions.

## Not performed

No packages were installed. No models were trained, no pipelines were run, and nothing was deployed.
