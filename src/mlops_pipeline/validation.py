from pathlib import Path
import numpy as np

import pandas as pd


EXPECTED_COLUMNS = [
    "sl_no",
    "gender",
    "ssc_p",
    "ssc_b",
    "hsc_p",
    "hsc_b",
    "hsc_s",
    "degree_p",
    "degree_t",
    "workex",
    "etest_p",
    "specialisation",
    "mba_p",
    "status",
]

CATEGORY_VALUES = {
    "gender": {"M", "F"},
    "ssc_b": {"Central", "Others"},
    "hsc_b": {"Central", "Others"},
    "hsc_s": {"Commerce", "Science", "Arts"},
    "degree_t": {"Sci&Tech", "Comm&Mgmt", "Others"},
    "workex": {"Yes", "No"},
    "specialisation": {"Mkt&HR", "Mkt&Fin"},
    "status": {"Placed", "Not Placed"},
}
NUMERIC_COLUMNS = ["sl_no", "ssc_p", "hsc_p", "degree_p", "etest_p", "mba_p"]
SCORE_COLUMNS = ["ssc_p", "hsc_p", "degree_p", "etest_p", "mba_p"]
REPORT_COLUMNS = ["column", "check", "failure_case", "index"]
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def validate_schema(df: pd.DataFrame, output_report_name: str = "schema_validation_errors.csv") -> bool:
    """Validate placement data and always write a current validation report."""
    failures: list[dict[str, object]] = []
    actual_columns = set(df.columns)

    if df.empty:
        failures.append({"column": None, "check": "non-empty dataset", "failure_case": "empty"})

    for column in EXPECTED_COLUMNS:
        if column not in actual_columns:
            failures.append({"column": column, "check": "required column", "failure_case": "missing"})
    for column in sorted(actual_columns - set(EXPECTED_COLUMNS)):
        failures.append({"column": column, "check": "unexpected column", "failure_case": "present"})

    if not df.empty:
        for column, allowed_values in CATEGORY_VALUES.items():
            if column not in df:
                continue
            invalid = df[column].notna() & ~df[column].astype(str).isin(allowed_values)
            for index, value in df.loc[invalid, column].items():
                failures.append(
                    {"column": column, "check": "allowed values", "failure_case": value, "index": index}
                )

        for column in NUMERIC_COLUMNS:
            if column not in df:
                continue
            values = pd.to_numeric(df[column], errors="coerce")
            invalid = values.isna() | ~np.isfinite(values)
            for index, value in df.loc[invalid, column].items():
                failures.append(
                    {"column": column, "check": "numeric and non-null", "failure_case": value, "index": index}
                )
            if column in SCORE_COLUMNS:
                invalid_range = values.notna() & ~values.between(0, 100)
                for index, value in df.loc[invalid_range, column].items():
                    failures.append(
                        {"column": column, "check": "score between 0 and 100", "failure_case": value, "index": index}
                    )

        for column in ("sl_no", "status"):
            if column in df and df[column].isna().any():
                for index in df.index[df[column].isna()]:
                    failures.append(
                        {"column": column, "check": "non-null", "failure_case": None, "index": index}
                    )

        if "sl_no" in df and df["sl_no"].duplicated().any():
            for index in df.index[df["sl_no"].duplicated(keep=False)]:
                failures.append(
                    {"column": "sl_no", "check": "unique identifier", "failure_case": df.at[index, "sl_no"], "index": index}
                )

    report_path = Path(output_report_name)
    if not report_path.is_absolute():
        if report_path.parts and report_path.parts[0] == "artifacts":
            report_path = PROJECT_ROOT / report_path
        else:
            report_path = PROJECT_ROOT / "artifacts" / report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(failures, columns=REPORT_COLUMNS).to_csv(report_path, index=False)

    if not failures:
        print(f"[SUCCESS] Placement schema validation passed ({len(df)} rows).")
        return True

    print(f"[ERROR] Placement schema validation failed; see {report_path}.")
    return False
