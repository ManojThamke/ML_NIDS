import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------
# PATH CONFIGURATION (ROBUST & PORTABLE)
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

JSON_FILE = BASE_DIR / "evaluation-engine" / "export" / "evaluation_metrics.json"
OUTPUT_DIR = BASE_DIR / "docs" / "phase2_charts_ieee"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "Fig_4_Confusion_Matrix_Realtime.png"

# --------------------------------------------------
# LOAD CONFUSION MATRIX DATA
# --------------------------------------------------
with open(JSON_FILE, "r") as f:
    data = json.load(f)

cm = data["confusionMatrix"]

TN = cm["TN"]
FP = cm["FP"]
FN = cm["FN"]
TP = cm["TP"]

confusion_matrix = np.array([
    [TN, FP],
    [FN, TP]
])

labels = ["BENIGN", "ATTACK"]

# --------------------------------------------------
# IEEE-SAFE CONFUSION MATRIX PLOT
# --------------------------------------------------
plt.figure(figsize=(4.6, 4.0))  # IEEE 2-column friendly
ax = plt.gca()

im = ax.imshow(confusion_matrix, cmap="Blues")

# Adaptive text color for readability
max_val = confusion_matrix.max()

for i in range(2):
    for j in range(2):
        value = confusion_matrix[i, j]
        text_color = "white" if value > max_val * 0.5 else "#2b2b2b"
        ax.text(
            j, i,
            f"{value}",
            ha="center",
            va="center",
            fontsize=11,
            color=text_color
        )

# Axis labels and ticks
ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(labels, fontsize=10)
ax.set_yticklabels(labels, fontsize=10)

ax.set_xlabel("Predicted Label", fontsize=11)
ax.set_ylabel("Actual Label", fontsize=11)

ax.set_title(
    "Confusion Matrix of Real-Time Intrusion Detection",
    fontsize=12,
    pad=6
)

# Clean IEEE look (no borders)
for spine in ax.spines.values():
    spine.set_visible(False)

# --------------------------------------------------
# SAVE ONLY (NO DISPLAY)
# --------------------------------------------------
plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
plt.close()

print(f"[OK] Confusion matrix saved at: {OUTPUT_FILE}")
