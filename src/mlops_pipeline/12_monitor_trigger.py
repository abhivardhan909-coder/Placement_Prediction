import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
NEW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "new_placement_data.csv"
PIPELINE_SCRIPT = PROJECT_ROOT / "src" / "mlops_pipeline" / "placement_prediction_pipeline.py"
TRIGGER_REPORT = PROJECT_ROOT / "outputs" / "monitoring" / "monitor_trigger_report.json"


def run_monitor_trigger() -> bool:
    new_data_present = NEW_DATA_PATH.is_file()
    report = {
        "status": "new_data_detected" if new_data_present else "no_new_data",
        "new_data_present": new_data_present,
        "pipeline_called": new_data_present,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if new_data_present:
        result = subprocess.run(
            [sys.executable, str(PIPELINE_SCRIPT)],
            cwd=PROJECT_ROOT,
            check=False,
        )
        report["pipeline_exit_code"] = result.returncode
        report["status"] = "pipeline_completed" if result.returncode == 0 else "pipeline_failed"

    TRIGGER_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with TRIGGER_REPORT.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)
    print(f"[INFO] Placement data monitoring result: {report['status']}")
    print(f"[INFO] Report written to {TRIGGER_REPORT}")
    return report["status"] != "pipeline_failed"


if __name__ == "__main__":
    sys.exit(0 if run_monitor_trigger() else 1)
