
import json
from pathlib import Path

import pandas as pd
import streamlit as st

LOG_FILE = Path("/app/logs/inference/inference_log.jsonl")

st.set_page_config(
    page_title="Churn Model Monitoring",
    page_icon="📊",
    layout="wide"
)

st.title("Telco Customer Churn - Model Monitoring")


@st.cache_data
def load_logs():
    if not LOG_FILE.exists():
        return pd.DataFrame()

    records = []
    with LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return pd.DataFrame(records)


if st.button("Refresh Dashboard"):
    load_logs.clear()

df = load_logs()

if df.empty:
    st.warning("No inference logs found.")
    st.stop()

for col in ["prediction", "churn_probability", "latency_ms"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

total = len(df)
success = int((df["status"] == "success").sum())
failed = total - success

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Requests", total)
c2.metric("Successful Requests", success)
c3.metric("Failed Requests", failed)
c4.metric(
    "Average Latency",
    f"{df['latency_ms'].mean():.2f} ms"
)

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Prediction Distribution")
    st.bar_chart(df["prediction"].value_counts().sort_index())


with right:
    st.subheader("Churn Probability")

    if "churn_probability" in df.columns:
        probabilities = df["churn_probability"].dropna()

        if not probabilities.empty:
            histogram = pd.cut(
                probabilities,
                bins=10,
                include_lowest=True
            ).value_counts().sort_index()

            histogram.index = histogram.index.astype(str)

            st.bar_chart(histogram)
        else:
            st.info("No probability data available.")


# DATA DRIFT MONITORING
st.divider()
st.header("Data Drift Monitoring")

drift_report = Path(
    "/app/reports/data_drift/drift_report.html"
)

if drift_report.exists():
    st.success("Data drift report is available.")

    with open(drift_report, "r", encoding="utf-8") as file:
        html_content = file.read()

    st.download_button(
        label="Download Data Drift Report",
        data=html_content,
        file_name="drift_report.html",
        mime="text/html"
    )
else:
    st.warning(
        "Data drift report not available inside dashboard container."
    )
