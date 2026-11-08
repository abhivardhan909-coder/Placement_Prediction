import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_NAME = "placement-prediction-api:latest"


def run(command: list[str]) -> None:
    print(f"[RUN] {' '.join(command)}")
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def deploy() -> None:
    if not (PROJECT_ROOT / "deployment" / "model.pkl").exists():
        raise FileNotFoundError("Run 11_prepare_deployment.py before building the API image.")
    if not (PROJECT_ROOT / "deployment" / "preprocessor.pkl").exists():
        raise FileNotFoundError("Deployment preprocessor is missing.")

    run(["docker", "build", "--tag", IMAGE_NAME, "."])
    run(["kubectl", "apply", "-f", str(PROJECT_ROOT / "k8s" / "deployment.yaml")])
    run(["kubectl", "apply", "-f", str(PROJECT_ROOT / "k8s" / "service.yaml")])
    run(["kubectl", "rollout", "status", "deployment/placement-api", "--timeout=180s"])

    report_path = PROJECT_ROOT / "reports" / "deployment_automation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "status": "success",
                "image": IMAGE_NAME,
                "deployment": "placement-api",
                "service": "placement-api-service",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            file,
            indent=2,
        )
    print(f"[SUCCESS] Placement API deployed; report written to {report_path}.")


if __name__ == "__main__":
    try:
        deploy()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"[ERROR] Placement API deployment failed: {exc}", file=sys.stderr)
        sys.exit(1)
