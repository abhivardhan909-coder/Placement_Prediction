# Placement Prediction Run Summary

The current dataset is `data/raw/Placement_Data_Full_Class.csv` (215 rows).
The latest held-out evaluation contains 43 rows:

| Metric | Value |
|---|---:|
| Accuracy | 0.8837 |
| Precision | 0.9310 |
| Recall | 0.9000 |
| F1 score | 0.9153 |
| ROC-AUC | 0.9449 |

Run the complete workflow with:

```powershell
python .\src\mlops_pipeline\placement_prediction_pipeline.py
```

Docker and Kubernetes instructions are maintained in the project
[README](../README.md) and [runbook](../docs/RUNBOOK.md).
