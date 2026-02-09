import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ==================================================
# PATH CONFIGURATION
# ==================================================
BASE_DIR = Path(__file__).resolve().parent.parent

JSON_FILE = BASE_DIR / "evaluation-engine" / "export" / "evaluation_metrics1.json"
OUTPUT_DIR = BASE_DIR / "docs" / "realtime charts ieee"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==================================================
# LOAD REAL-TIME METRICS
# ==================================================
with open(JSON_FILE, "r") as f:
    data = json.load(f)

# ==================================================
# FIGURE 1: CONFUSION MATRIX (REAL-TIME)
# ==================================================
cm = data["confusionMatrix"]

TN, FP = cm["TN"], cm["FP"]
FN, TP = cm["FN"], cm["TP"]

conf_matrix = np.array([[TN, FP],
                         [FN, TP]])

labels = ["BENIGN", "ATTACK"]

plt.figure(figsize=(4.6, 4.0))
ax = plt.gca()
ax.imshow(conf_matrix, cmap="GnBu")

for i in range(2):
    for j in range(2):
        ax.text(j, i, f"{conf_matrix[i, j]}",
                ha="center", va="center",
                fontsize=11, color="#2b2b2b")

ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(labels, fontsize=10)
ax.set_yticklabels(labels, fontsize=10)

ax.set_xlabel("Predicted Label", fontsize=11)
ax.set_ylabel("Actual Label", fontsize=11)
ax.set_title("Confusion Matrix of Real-Time Intrusion Detection", fontsize=11)

for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "Fig_RealTime_Confusion_Matrix.png", dpi=300)
plt.close()

# ==================================================
# FIGURE 2: TRAFFIC DISTRIBUTION (BENIGN vs ATTACK)
# ==================================================
support = data["classificationMetrics"]["Support"]
class_labels = ["BENIGN", "ATTACK"]
class_counts = [support["BENIGN"], support["ATTACK"]]

plt.figure(figsize=(4.6, 3.6))
bars = plt.bar(class_labels, class_counts,
               color=["#4C72B0", "#DD8452"],
               width=0.6)

for bar in bars:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2,
             h, f"{int(h)}",
             ha="center", va="bottom",
             fontsize=9)

plt.ylabel("Number of Samples", fontsize=11)
plt.title("Real-Time Traffic Distribution", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.margins(y=0.15)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "Fig_RealTime_Traffic_Distribution.png", dpi=300)
plt.close()

# ==================================================
# FIGURE 3: DOMINANT MODEL CONTRIBUTION
# ==================================================
dominance = data["perModelAnalysis"]["Dominant Model Frequency"]

models = list(dominance.keys())
counts = list(dominance.values())

plt.figure(figsize=(5.2, 3.8))
plt.barh(models, counts, color="#55A868")

plt.xlabel("Dominant Predictions", fontsize=11)
plt.title("Dominant Model Contribution in Real-Time Detection", fontsize=10)
plt.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "Fig_RealTime_Model_Dominance.png", dpi=300)
plt.close()

# ==================================================
# FIGURE 4: REAL-TIME PERFORMANCE METRICS
# ==================================================
metrics = data["classificationMetrics"]

metric_labels = ["Accuracy", "Precision", "Recall", "F1-Score"]
metric_values = [
    metrics["Accuracy"] * 100,
    metrics["Precision"] * 100,
    metrics["Recall"] * 100,
    metrics["F1-Score"] * 100
]

plt.figure(figsize=(4.6, 3.6))
bars = plt.bar(metric_labels, metric_values,
               color="#C44E52",
               width=0.6)

for bar, val in zip(bars, metric_values):
    plt.text(bar.get_x() + bar.get_width() / 2,
             val, f"{val:.2f}%",
             ha="center", va="bottom",
             fontsize=9)

plt.ylabel("Percentage (%)", fontsize=11)
plt.ylim(0, 105)
plt.title("Real-Time Detection Performance Metrics", fontsize=11)
plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "Fig_RealTime_Performance_Metrics.png", dpi=300)
plt.close()

print("[OK] All IEEE real-time evaluation figures generated successfully.")
