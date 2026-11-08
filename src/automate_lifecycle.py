import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE_STAGE = PROJECT_ROOT / "src" / "mlops_pipeline" / "08_automate_lifecycle.py"


if __name__ == "__main__":
    result = subprocess.run([sys.executable, str(LIFECYCLE_STAGE)], cwd=PROJECT_ROOT, check=False)
    sys.exit(result.returncode)
