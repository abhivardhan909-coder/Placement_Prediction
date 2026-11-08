import argparse
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAGES = [
    ("Data Loading", "src/mlops_pipeline/01_load_data.py"),
    ("Raw Data Validation", "src/mlops_pipeline/02_validate_data.py"),
    ("Preprocessing", "src/mlops_pipeline/03_preprocessing.py"),
    ("Processed Output Validation", "src/mlops_pipeline/04_validate_outputs.py"),
    ("Training + MLflow + Model Registry", "src/mlops_pipeline/05_train_registry.py"),
    ("Model Evaluation", "src/mlops_pipeline/06_model_evaluation.py"),
    ("Model Quality Gate", "src/mlops_pipeline/07_quality_gate.py"),
    ("Automated Model Lifecycle", "src/mlops_pipeline/08_automate_lifecycle.py"),
    ("Deployment Update", "src/mlops_pipeline/deploy_if_promoted.py"),
    ("Production Inference", "src/mlops_pipeline/09_inference.py"),
]


def load_data_load_report():
    report_path = PROJECT_ROOT / "artifacts" / "data_load_report.json"
    if not report_path.exists():
        raise FileNotFoundError(f"Data load report not found: {report_path}")

    with report_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_pipeline(force=False):
    print("[INFO] Starting Placement Prediction MLOps Pipeline")
    run_log = {"pipeline": "Placement Prediction MLOps", "stages": [], "force": force}

    for stage_index, (stage_name, script_path) in enumerate(STAGES):
        print(f"\n{'=' * 70}\nRUNNING: {stage_name}\n{'=' * 70}")
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / script_path)],
            cwd=PROJECT_ROOT,
            check=False,
        )
        status = "PASSED" if result.returncode == 0 else "FAILED"
        run_log["stages"].append(
            {"stage": stage_name, "status": status, "exit_code": result.returncode}
        )
        print(f"--> {stage_name}: {status}")

        if result.returncode != 0:
            print("[HALT] Pipeline stopped because this stage failed.")
            run_log["overall_status"] = "FAILED"
            break

        if stage_index == 0:
            data_status = load_data_load_report().get("status")
            if data_status in {"already_ingested", "no_new_data"}:
                print(f"[INFO] Data load status: {data_status}; using current dataset.")
            elif data_status == "ingested":
                print("[INFO] New placement data was successfully ingested.")
            else:
                print(f"[ERROR] Unexpected data load status: {data_status}")
                print("[HALT] Pipeline stopped because the ingestion state is unknown.")
                run_log["overall_status"] = "FAILED"
                break

    all_passed = len(run_log["stages"]) == len(STAGES) and all(
        stage["status"] == "PASSED" for stage in run_log["stages"]
    )
    if all_passed:
        run_log["overall_status"] = "PASSED"

    log_path = PROJECT_ROOT / "logs" / "placement_prediction_pipeline_run_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as file:
        json.dump(run_log, file, indent=4)

    if run_log["overall_status"] == "PASSED":
        print("[SUCCESS] Placement Prediction MLOps Pipeline completed successfully.")
    else:
        print("[ERROR] Placement Prediction MLOps Pipeline failed.")
    print(f"[INFO] Run log: {log_path}")

    return run_log["overall_status"] == "PASSED"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the Placement Prediction MLOps pipeline."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Retained for compatibility with existing workflows.",
    )
    args = parser.parse_args()
    sys.exit(0 if run_pipeline(force=args.force) else 1)
