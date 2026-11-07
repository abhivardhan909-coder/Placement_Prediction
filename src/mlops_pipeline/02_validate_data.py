import os
import sys
from pathlib import Path

import pandas as pd
import yaml

from validation import validate_schema


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

def main():
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    data_path = PROJECT_ROOT / config["data"]["raw_path"]

    if not os.path.exists(data_path):
        print(f"[ERROR] Target file not found at: {data_path}")
        sys.exit(1)

    raw_df = pd.read_csv(data_path)
    report_path = PROJECT_ROOT / "artifacts" / "baseline_validation.csv"
    passed = validate_schema(raw_df, output_report_name=str(report_path))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
