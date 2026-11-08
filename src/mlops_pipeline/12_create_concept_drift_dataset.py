from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURES_PATH = PROJECT_ROOT / "data" / "monitoring" / "drift" / "evolved_data.csv"
LABELS_PATH = PROJECT_ROOT / "data" / "processed" / "y_test.npy"
OUTPUT_PATH = PROJECT_ROOT / "data" / "monitoring" / "drift" / "evolved_labeled_data.csv"
RANDOM_SEED = 42


def create_concept_drift_dataset() -> pd.DataFrame:
    if not FEATURES_PATH.exists() or not LABELS_PATH.exists():
        raise FileNotFoundError("Generate evolved placement features and the test split first.")

    features = pd.read_csv(FEATURES_PATH)
    labels = np.load(LABELS_PATH).astype(int)
    if len(features) != len(labels):
        raise ValueError(f"Feature/label mismatch: X={len(features)}, y={len(labels)}")

    rng = np.random.default_rng(RANDOM_SEED)
    evolved_labels = labels.copy()
    changed_count = max(1, int(len(labels) * 0.15))
    changed_indices = rng.choice(len(labels), size=changed_count, replace=False)
    evolved_labels[changed_indices] = 1 - evolved_labels[changed_indices]

    result = features.copy()
    result["status"] = np.where(evolved_labels == 1, "Placed", "Not Placed")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False)
    print(f"[SUCCESS] Concept-drift placement dataset saved to {OUTPUT_PATH}.")
    return result


if __name__ == "__main__":
    create_concept_drift_dataset()
