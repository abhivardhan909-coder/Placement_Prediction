import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.mlops_pipeline.validation import validate_schema


def simulate_corrupted_data(data: pd.DataFrame) -> pd.DataFrame:
    corrupted = data.copy()
    corrupted.loc[0, "ssc_p"] = -5
    corrupted.loc[1, "gender"] = "Unknown"
    corrupted.loc[2, "status"] = "Pending"
    corrupted["hsc_p"] = corrupted["hsc_p"].astype(object)
    corrupted.loc[3, "hsc_p"] = "INVALID_NUMBER"
    corrupted["unexpected_column"] = 123
    return corrupted.drop(columns=["gender"])


if __name__ == "__main__":
    dataset_path = PROJECT_ROOT / "data" / "raw" / "Placement_Data_Full_Class.csv"
    raw_data = pd.read_csv(dataset_path)
    corrupted_data = simulate_corrupted_data(raw_data)
    report_path = PROJECT_ROOT / "artifacts" / "corrupted_simulation_errors.csv"
    validate_schema(corrupted_data, output_report_name=str(report_path))
