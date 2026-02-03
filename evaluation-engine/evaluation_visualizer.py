import json
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
from pathlib import Path

# =====================================================
# PATH CONFIG
# =====================================================
BASE_DIR = Path(__file__).parent

INPUT_JSON = BASE_DIR / "export" / "evaluation_metrics.json"

TABLE_DIR = BASE_DIR / "reports" / "tables"
CHART_DIR = BASE_DIR / "reports" / "charts"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["figure.figsize"] = (10, 6)

# =====================================================
# LOAD JSON
# =====================================================
with open(INPUT_JSON, "r") as f:
    data = json.load(f)

# =====================================================
# 1. CONFUSION MATRIX
# =====================================================
cm = data["confusionMatrix"]

cm_df = pd.DataFrame({
    "Metric": ["TP", "FP", "TN", "FN", "FPR", "FNR"],
    "Value": [
        cm["TP"],
        cm["FP"],
        cm["TN"],
        cm["FN"],
        cm["False Positive Rate"],
        cm["False Negative Rate"]
    ]
})

print("\nCONFUSION MATRIX")
print(tabulate(cm_df, headers="keys", tablefmt="grid"))

cm_df.to_csv(TABLE_DIR / "confusion_matrix.csv", index=False)

# =====================================================
# 2. CLASSIFICATION METRICS
# =====================================================
metrics = data["classificationMetrics"]

metrics_df = pd.DataFrame({
    "Metric": ["Accuracy", "Precision", "Recall", "F1-Score"],
    "Value": [
        metrics["Accuracy"],
        metrics["Precision"],
        metrics["Recall"],
        metrics["F1-Score"]
    ]
})

print("\nCLASSIFICATION METRICS")
print(tabulate(metrics_df, headers="keys", tablefmt="grid"))

metrics_df.to_csv(TABLE_DIR / "classification_metrics.csv", index=False)

# =====================================================
# 3. CLASS SUPPORT
# =====================================================
support_df = pd.DataFrame.from_dict(
    metrics["Support"], orient="index", columns=["Samples"]
)

print("\nCLASS SUPPORT")
print(tabulate(support_df, headers="keys", tablefmt="grid"))

support_df.to_csv(TABLE_DIR / "class_support.csv")

# =====================================================
# 4. MODEL DOMINANCE
# =====================================================
dominance = data["perModelAnalysis"]["Dominant Model Frequency"]

dom_df = pd.DataFrame(
    dominance.items(), columns=["Model", "Dominance Count"]
).sort_values(by="Dominance Count", ascending=False)

plt.figure()
plt.bar(dom_df["Model"], dom_df["Dominance Count"])
plt.xticks(rotation=45, ha="right")
plt.title("Model Dominance Frequency")
plt.ylabel("Prediction Count")
plt.tight_layout()
plt.savefig(CHART_DIR / "model_dominance.png")
plt.close()

dom_df.to_csv(TABLE_DIR / "model_dominance.csv", index=False)

# =====================================================
# 5. AVERAGE CONFIDENCE PER MODEL
# =====================================================
confidence = data["perModelAnalysis"]["Average Confidence Per Model"]

conf_df = pd.DataFrame(
    confidence.items(), columns=["Model", "Average Confidence"]
).sort_values(by="Average Confidence", ascending=False)

plt.figure()
plt.bar(conf_df["Model"], conf_df["Average Confidence"])
plt.xticks(rotation=45, ha="right")
plt.title("Average Confidence per Model")
plt.ylabel("Confidence")
plt.tight_layout()
plt.savefig(CHART_DIR / "avg_confidence_per_model.png")
plt.close()

conf_df.to_csv(TABLE_DIR / "avg_confidence_per_model.csv", index=False)

# =====================================================
# 6. ENSEMBLE COMPARISON
# =====================================================
ensemble = data["ensembleComparison"]

ensemble_df = pd.DataFrame({
    "Type": ["Ensemble", "Best Model"],
    "Confidence": [
        ensemble["Average Ensemble Confidence"],
        ensemble["Average Best Model Confidence"]
    ]
})

plt.figure()
plt.bar(ensemble_df["Type"], ensemble_df["Confidence"])
plt.title("Ensemble vs Best Model Confidence")
plt.ylabel("Confidence")
plt.tight_layout()
plt.savefig(CHART_DIR / "ensemble_vs_best_model.png")
plt.close()

ensemble_df.to_csv(TABLE_DIR / "ensemble_comparison.csv", index=False)

# =====================================================
# 7. ALERT NOISE
# =====================================================
alert_noise = ensemble["Alert Noise"]

noise_df = pd.DataFrame({
    "Metric": [
        "Low Confidence ATTACK Alerts",
        "Total ATTACK Alerts",
        "Noise Ratio"
    ],
    "Value": [
        alert_noise["Low Confidence ATTACK Alerts"],
        alert_noise["Total ATTACK Alerts"],
        alert_noise["Noise Ratio"]
    ]
})

print("\nALERT NOISE")
print(tabulate(noise_df, headers="keys", tablefmt="grid"))

plt.figure()
plt.bar(
    ["Low Confidence", "Valid Alerts"],
    [
        alert_noise["Low Confidence ATTACK Alerts"],
        alert_noise["Total ATTACK Alerts"]
        - alert_noise["Low Confidence ATTACK Alerts"]
    ]
)
plt.title("Attack Alert Noise Distribution")
plt.ylabel("Alert Count")
plt.tight_layout()
plt.savefig(CHART_DIR / "alert_noise.png")
plt.close()

noise_df.to_csv(TABLE_DIR / "alert_noise.csv", index=False)

# =====================================================
# 8. THRESHOLD PROXIMITY
# =====================================================
threshold = data["perModelAnalysis"]["Threshold Proximity"]

threshold_df = pd.DataFrame({
    "Metric": ["Near Threshold", "Total Predictions", "Percentage"],
    "Value": [
        threshold["near_threshold_count"],
        threshold["total_predictions"],
        threshold["percentage"]
    ]
})

print("\nTHRESHOLD PROXIMITY")
print(tabulate(threshold_df, headers="keys", tablefmt="grid"))

threshold_df.to_csv(TABLE_DIR / "threshold_proximity.csv", index=False)

print("\n✅ Reports generated successfully")
print("📁 Tables  →", TABLE_DIR)
print("📊 Charts  →", CHART_DIR)
