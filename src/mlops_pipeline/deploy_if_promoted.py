
import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE_REPORT = PROJECT_ROOT / "reports" / "lifecycle_report.json"
PREPARE_SCRIPT = PROJECT_ROOT / "src" / "mlops_pipeline" / "11_prepare_deployment.py"
DEPLOY_SCRIPT = PROJECT_ROOT / "deployment" / "deploy_production.py"


def load_lifecycle_report():
    if not LIFECYCLE_REPORT.exists():
        raise FileNotFoundError(
            f"Lifecycle report not found: {LIFECYCLE_REPORT}"
        )

    with LIFECYCLE_REPORT.open("r", encoding="utf-8") as f:
        return json.load(f)


def run_script(script_path):
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT
    )
    return result.returncode == 0


def main():
    print("=" * 70)
    print("DEPLOY IF MODEL WAS PROMOTED")
    print("=" * 70)

    report = load_lifecycle_report()

    promoted = report.get("promoted", False)
    candidate_version = report.get("candidate_version")
    production_version = report.get("production_version_after")

    print(f"[INFO] Candidate version : {candidate_version}")
    print(f"[INFO] Promoted          : {promoted}")
    print(f"[INFO] Production version: {production_version}")

    if not promoted:
        print("[INFO] Model was not promoted.")
        print("[INFO] Existing production model will be retained.")
        print("[SUCCESS] Deployment skipped successfully.")
        return True

    print(f"[INFO] Model Version {candidate_version} was promoted.")
    print("[INFO] Preparing production deployment artifacts...")

    if not run_script(PREPARE_SCRIPT):
        print("[ERROR] Deployment preparation failed.")
        return False

    print("[SUCCESS] Deployment artifacts prepared.")

    # GitHub Actions runners cannot access local Docker Desktop
    # Kubernetes clusters. Validate and archive the bundle in CI.
    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        deployment_dir = PROJECT_ROOT / "deployment"

        required_files = [
            deployment_dir / "model.pkl",
            deployment_dir / "preprocessor.pkl",
            deployment_dir / "model_metadata.json",
        ]

        missing_files = [
            str(path) for path in required_files if not path.is_file()
        ]

        if missing_files:
            print("[ERROR] Deployment bundle is incomplete:")
            for path in missing_files:
                print(f" - {path}")
            return False

        print("[SUCCESS] Production model bundle validated.")
        print("[INFO] Running inside GitHub Actions.")
        print("[INFO] Local Docker/Kubernetes deployment skipped.")
        print("[SUCCESS] CI deployment preparation completed.")
        return True

    print("[INFO] Running on local deployment environment.")
    print("[INFO] Starting Docker/Kubernetes production deployment...")

    if not run_script(DEPLOY_SCRIPT):
        print("[ERROR] Production deployment failed.")
        return False

    print("[SUCCESS] Production deployment completed.")
    return True


if __name__ == "__main__":
    try:
        sys.exit(0 if main() else 1)
    except Exception as exc:
        print(f"[ERROR] Deployment stage failed: {exc}")
        sys.exit(1)
