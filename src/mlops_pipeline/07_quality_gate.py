import json
import os
import sys
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def run_quality_gate():
    print("[INFO] Starting Model Quality Gate...")

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    report_path = PROJECT_ROOT / config["paths"]["evaluation_report"]
    metric_name = config["quality_gate"]["metric"]
    minimum_value = float(config["quality_gate"]["minimum_value"])

    try:
        with report_path.open("r", encoding="utf-8") as f:
            report = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Evaluation report not found: {report_path}")
        return False

    actual_value = float(report["metrics"].get(metric_name, 0.0))
    passed = actual_value >= minimum_value

    print(
        f"[INFO] Quality Gate: {metric_name}={actual_value:.4f} | "
        f"required>={minimum_value:.4f}"
    )

    gate_report = {
        "stage": "Lab 8 - Model Quality Gate",
        "metric": metric_name,
        "minimum_value": minimum_value,
        "actual_value": actual_value,
        "status": "PASSED" if passed else "FAILED",
    }

    gate_report_path = PROJECT_ROOT / config["paths"]["quality_gate_report"]
    gate_report_path.parent.mkdir(parents=True, exist_ok=True)
    with gate_report_path.open("w", encoding="utf-8") as f:
        json.dump(gate_report, f, indent=4)

    if passed:
        print("[SUCCESS] Model Quality Gate PASSED.")
    else:
        print("[ERROR] Model Quality Gate FAILED. Pipeline will stop before promotion.")

    return passed


if __name__ == "__main__":
    passed = run_quality_gate()
    sys.exit(0 if passed else 1)
