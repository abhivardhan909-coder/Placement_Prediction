from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "X_train_raw.csv"
TRAIN_LABELS_PATH = PROJECT_ROOT / "data" / "processed" / "y_train.npy"
TEST_FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "X_test_raw.csv"
NEW_BATCH_PATH = PROJECT_ROOT / "data" / "monitoring" / "drift" / "post_drift_training_data.csv"
UPDATED_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "updated_training_data.csv"
SUMMARY_PATH = PROJECT_ROOT / "outputs" / "retraining" / "updated_dataset_summary.csv"
RANDOM_SEED = 42


def create_updated_dataset() -> pd.DataFrame:
    required_paths = (TRAIN_FEATURES_PATH, TRAIN_LABELS_PATH, TEST_FEATURES_PATH)
    if any(not path.exists() for path in required_paths):
        raise FileNotFoundError("Run placement preprocessing before creating retraining data.")

    rng = np.random.default_rng(RANDOM_SEED)
    train_features = pd.read_csv(TRAIN_FEATURES_PATH)
    train_labels = np.load(TRAIN_LABELS_PATH).astype(int)
    test_features = pd.read_csv(TEST_FEATURES_PATH)
    if len(train_features) != len(train_labels):
        raise ValueError("Training feature/label count mismatch.")

    batch_size = min(len(train_features), max(1, len(test_features)))
    indices = rng.choice(len(train_features), size=batch_size, replace=True)
    new_features = train_features.iloc[indices].copy().reset_index(drop=True)
    new_labels = train_labels[indices].copy()

    for column in ("ssc_p", "hsc_p", "degree_p", "etest_p", "mba_p"):
        new_features[column] = (new_features[column] + rng.normal(3, 6, batch_size)).clip(0, 100)

    category_options = {
        "gender": ["M", "F"],
        "hsc_s": ["Commerce", "Science", "Arts"],
        "degree_t": ["Sci&Tech", "Comm&Mgmt", "Others"],
        "workex": ["Yes", "No"],
        "specialisation": ["Mkt&HR", "Mkt&Fin"],
    }
    for column, values in category_options.items():
        new_features[column] = rng.choice(values, size=batch_size)

    lower_scores = new_features["ssc_p"] < new_features["ssc_p"].median()
    candidates = np.flatnonzero(lower_scores & (new_labels == 1))
    flip_count = min(len(candidates), int(len(candidates) * 0.2))
    if flip_count:
        new_labels[rng.choice(candidates, size=flip_count, replace=False)] = 0

    overlap = set(
        pd.util.hash_pandas_object(test_features, index=False).astype("uint64")
    ) & set(pd.util.hash_pandas_object(new_features, index=False).astype("uint64"))
    if overlap:
        raise ValueError("Generated batch contains exact feature rows from the held-out test set.")

    original = train_features.copy()
    original["status"] = train_labels
    batch = new_features.copy()
    batch["status"] = new_labels
    updated = pd.concat([original, batch], ignore_index=True)

    NEW_BATCH_PATH.parent.mkdir(parents=True, exist_ok=True)
    UPDATED_DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    batch.to_csv(NEW_BATCH_PATH, index=False)
    updated.to_csv(UPDATED_DATASET_PATH, index=False)

    summary = pd.DataFrame(
        [
            {
                "dataset": name,
                "rows": len(data),
                "placed": int((data["status"] == 1).sum()),
                "not_placed": int((data["status"] == 0).sum()),
                "placement_rate": float(data["status"].mean()),
            }
            for name, data in (
                ("original_training", original),
                ("post_drift_batch", batch),
                ("updated_training", updated),
            )
        ]
    )
    summary.to_csv(SUMMARY_PATH, index=False)
    print(f"[SUCCESS] Placement retraining data written to {UPDATED_DATASET_PATH}.")
    return updated


if __name__ == "__main__":
    create_updated_dataset()
