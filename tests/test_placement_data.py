from pathlib import Path

import pandas as pd

from src.mlops_pipeline.validation import validate_schema


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_placement_dataset_schema_and_labels(tmp_path):
    dataset_path = PROJECT_ROOT / "data" / "raw" / "Placement_Data_Full_Class.csv"
    data = pd.read_csv(dataset_path)

    assert len(data) == 215
    assert validate_schema(data, str(tmp_path / "schema_validation_errors.csv"))
    assert set(data["status"].unique()) == {"Placed", "Not Placed"}
    assert data["sl_no"].is_unique


def test_successful_validation_replaces_stale_report(tmp_path):
    dataset_path = PROJECT_ROOT / "data" / "raw" / "Placement_Data_Full_Class.csv"
    report_path = tmp_path / "baseline_validation.csv"
    report_path.write_text("churn_probability\n0.5\n", encoding="utf-8")

    assert validate_schema(pd.read_csv(dataset_path), str(report_path))
    report = pd.read_csv(report_path)

    assert report.empty
    assert list(report.columns) == ["column", "check", "failure_case", "index"]
