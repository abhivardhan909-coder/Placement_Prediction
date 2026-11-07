import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

def execute_pipeline():
    print("[INFO] =========================================")
    print("[INFO] Starting Lab 4: MLflow Experiment Tracking")
    print("[INFO] =========================================")
    
    scripts = [
        PROJECT_ROOT / "src" / "preprocess.py",
        PROJECT_ROOT / "src" / "train_mlflow.py",
        PROJECT_ROOT / "src" / "validate_reproducibility.py",
    ]
    
    for script in scripts:
        relative_script = script.relative_to(PROJECT_ROOT)
        print(f"\n[INFO] ---> Executing {relative_script}...")
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=PROJECT_ROOT,
        )
        
        if result.returncode != 0:
            print(f"[ERROR] Pipeline halted. {relative_script} failed.")
            sys.exit(1)
            
    print("\n[SUCCESS] Lab 4 Pipeline fully executed!")

if __name__ == "__main__":
    execute_pipeline()
