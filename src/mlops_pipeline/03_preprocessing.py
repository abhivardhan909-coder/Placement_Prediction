import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def load_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def encode_target(values: pd.Series, config: dict) -> pd.Series:
    target_mapping = config["data"]["target_mapping"]
    encoded = values.map(target_mapping)
    if encoded.isna().any():
        unexpected = sorted(values[encoded.isna()].astype(str).unique())
        raise ValueError(f"Unknown target label(s): {unexpected}")
    return encoded.astype(np.int64)


def split_raw_data(df: pd.DataFrame, config: dict, processed_dir: Path):
    target_column = config["data"]["target_column"]
    id_column = config["data"]["id_column"]
    test_ids_path = processed_dir / "test_ids.csv"

    test_ids = set()
    if test_ids_path.exists():
        saved_ids = pd.read_csv(test_ids_path)
        if id_column in saved_ids.columns:
            test_ids = set(saved_ids[id_column].astype(str)) & set(df[id_column].astype(str))

    if not test_ids:
        _, test_rows = train_test_split(
            df,
            test_size=config["split"]["test_size"],
            random_state=config["split"]["random_state"],
            stratify=encode_target(df[target_column], config),
        )
        test_ids = set(test_rows[id_column].astype(str))
        pd.DataFrame({id_column: sorted(test_ids)}).to_csv(test_ids_path, index=False)

    id_values = df[id_column].astype(str)
    test_mask = id_values.isin(test_ids)
    if not test_mask.any() or test_mask.all():
        raise ValueError("The fixed test split must contain both test and training rows.")

    test_df = df.loc[test_mask].copy()
    train_df = df.loc[~test_mask].copy()
    feature_columns = [column for column in df.columns if column not in {id_column, target_column}]

    X_train = train_df.loc[:, feature_columns]
    X_test = test_df.loc[:, feature_columns]
    y_train = encode_target(train_df[target_column], config)
    y_test = encode_target(test_df[target_column], config)
    return X_train, X_test, y_train, y_test


def build_preprocessor(X_train: pd.DataFrame):
    categorical_columns = X_train.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    numeric_columns = X_train.select_dtypes(include=["number"]).columns.tolist()

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("one_hot_encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ]
    )
    return preprocessor, categorical_columns, numeric_columns


def run_preprocessing():
    config = load_config()
    data_config = config["data"]
    raw_path = PROJECT_ROOT / data_config["raw_path"]
    processed_dir = PROJECT_ROOT / data_config["processed_dir"]
    preprocessor_path = PROJECT_ROOT / config["paths"]["preprocessor"]

    if not raw_path.exists():
        raise FileNotFoundError(f"Placement dataset not found: {raw_path}")

    processed_dir.mkdir(parents=True, exist_ok=True)
    preprocessor_path.parent.mkdir(parents=True, exist_ok=True)
    raw_df = pd.read_csv(raw_path)
    X_train, X_test, y_train, y_test = split_raw_data(raw_df, config, processed_dir)
    preprocessor, categorical_columns, numeric_columns = build_preprocessor(X_train)

    X_train_final = preprocessor.fit_transform(X_train)
    X_test_final = preprocessor.transform(X_test)

    np.save(processed_dir / "X_train_final.npy", X_train_final)
    np.save(processed_dir / "X_test_final.npy", X_test_final)
    np.save(processed_dir / "y_train.npy", y_train.to_numpy())
    np.save(processed_dir / "y_test.npy", y_test.to_numpy())
    X_train.to_csv(processed_dir / "X_train_raw.csv", index=False)
    X_test.to_csv(processed_dir / "X_test_raw.csv", index=False)
    joblib.dump(preprocessor, preprocessor_path)

    metadata = {
        "dataset_name": "Placement Prediction",
        "target_column": data_config["target_column"],
        "target_mapping": data_config["target_mapping"],
        "train_shape_raw": list(X_train.shape),
        "test_shape_raw": list(X_test.shape),
        "train_shape_transformed": list(X_train_final.shape),
        "test_shape_transformed": list(X_test_final.shape),
        "categorical_features": categorical_columns,
        "numerical_features": numeric_columns,
        "test_size": config["split"]["test_size"],
        "random_state": config["split"]["random_state"],
        "fixed_test_ids_path": str((processed_dir / "test_ids.csv").relative_to(PROJECT_ROOT)),
    }
    with (processed_dir / "dataset_metadata.json").open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    print(f"[SUCCESS] Preprocessed placement data: {X_train_final.shape[0]} train, {X_test_final.shape[0]} test.")
    return True


if __name__ == "__main__":
    sys.exit(0 if run_preprocessing() else 1)
