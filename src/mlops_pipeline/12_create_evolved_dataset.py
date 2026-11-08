from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = PROJECT_ROOT / "data" / "processed" / "X_test_raw.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "monitoring" / "drift" / "evolved_data.csv"
RANDOM_SEED = 42


def create_evolved_dataset() -> pd.DataFrame:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Placement test features not found: {SOURCE_PATH}")

    rng = np.random.default_rng(RANDOM_SEED)
    data = pd.read_csv(SOURCE_PATH)
    for column in ("ssc_p", "hsc_p", "degree_p", "etest_p", "mba_p"):
        data[column] = (data[column] + rng.normal(4, 7, len(data))).clip(0, 100)

    categorical_options = {
        "gender": (["M", "F"], [0.55, 0.45]),
        "hsc_s": (["Commerce", "Science", "Arts"], [0.50, 0.35, 0.15]),
        "degree_t": (["Sci&Tech", "Comm&Mgmt", "Others"], [0.45, 0.40, 0.15]),
        "workex": (["Yes", "No"], [0.45, 0.55]),
        "specialisation": (["Mkt&HR", "Mkt&Fin"], [0.40, 0.60]),
    }
    for column, (values, probabilities) in categorical_options.items():
        data[column] = rng.choice(values, size=len(data), p=probabilities)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUTPUT_PATH, index=False)
    print(f"[SUCCESS] Evolved placement feature data saved to {OUTPUT_PATH} ({len(data)} rows).")
    return data


if __name__ == "__main__":
    create_evolved_dataset()
