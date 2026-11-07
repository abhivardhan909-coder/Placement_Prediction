import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

def execute_pipeline():
    print("[INFO] =========================================")
    print("[INFO] Starting Lab 3: Baseline ML Pipeline")
    print("[INFO] =========================================")
    
    scripts = [
        PROJECT_ROOT / "src" / "preprocess.py",
        PROJECT_ROOT / "src" / "train.py",
        PROJECT_ROOT / "src" / "evaluate.py",
    ]
    
    for script in scripts:
        relative_script = script.relative_to(PROJECT_ROOT)
        print(f"\n[INFO] ---> Executing {relative_script}...")
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=PROJECT_ROOT,
        )
        
        if result.returncode != 0:
            print(f"[ERROR] Pipeline halted. {relative_script} failed with exit code {result.returncode}.")
            sys.exit(1)
            
    print("\n[SUCCESS] Lab 3 Pipeline fully executed!")

if __name__ == "__main__":
    execute_pipeline()
