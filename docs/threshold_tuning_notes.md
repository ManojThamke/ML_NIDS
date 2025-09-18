# Threshold tuning notes

This file contains results for different probability thresholds computed from your realtime predictions log.

- Source log (backup): `C:\Users\Manoj\Downloads\BE Project\ML_NIDS\logs\realtime_predictions.csv.bak`
- Cleaned rows read: 2046

## Results table

|   threshold |   alerts |   alert_rate |
|------------:|---------:|-------------:|
|        0.01 |        0 |            0 |
|        0.05 |        0 |            0 |
|        0.1  |        0 |            0 |
|        0.5  |        0 |            0 |
|        0.6  |        0 |            0 |
|        0.7  |        0 |            0 |
|        0.8  |        0 |            0 |
|        0.9  |        0 |            0 |

**Note:** No ground-truth (`true_label`) column found in the log. To compute precision/recall, label attack rows (e.g. by dst_port) and add `true_label` column to the log or produce a labeled copy.
