
from pathlib import Path

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset

# Project root directory
ROOT = Path(__file__).resolve().parents[2]

# Compare the training features with the generated evolved placement features.
REFERENCE_FILE = ROOT / "data" / "processed" / "X_train_raw.csv"
CURRENT_FILE = ROOT / "data" / "monitoring" / "drift" / "evolved_data.csv"

# Report output directory
OUTPUT_DIR = ROOT / "reports/data_drift"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Check dataset files
if not REFERENCE_FILE.exists():
    raise FileNotFoundError(f"Reference dataset not found: {REFERENCE_FILE}")

if not CURRENT_FILE.exists():
    raise FileNotFoundError(f"Current dataset not found: {CURRENT_FILE}")

# Load datasets
reference = pd.read_csv(REFERENCE_FILE)
current = pd.read_csv(CURRENT_FILE)

# Keep matching columns in the same order
common_columns = [
    column for column in reference.columns
    if column in current.columns
]

reference = reference[common_columns]
current = current[common_columns]

# Generate data drift report
report = Report([
    DataDriftPreset()
])

result = report.run(
    reference_data=reference,
    current_data=current
)

# Save HTML report
report_path = OUTPUT_DIR / "drift_report.html"
result.save_html(str(report_path))

print("\nDATA DRIFT ANALYSIS COMPLETED")
print("--------------------------------")
print("Reference dataset: X_train_raw.csv")
print("Current dataset: evolved_data.csv")
print("Reference rows:", len(reference))
print("Current rows:", len(current))
print("Features compared:", len(common_columns))
print("Report saved at:", report_path)
