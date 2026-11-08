import pandas as pd


def clean_prediction_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop optional dataset identifiers/labels before transforming features."""
    df = df.copy()
    return df.drop(columns=["sl_no", "status"], errors="ignore")
