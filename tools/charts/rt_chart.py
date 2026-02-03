import matplotlib.pyplot as plt
import os
import numpy as np

# ----------------------------------
# OUTPUT PATH
# ----------------------------------
OUTPUT_DIR = os.path.join("docs", "phase2_charts_ieee")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------
# REAL-TIME CONFUSION DATA
# ----------------------------------
labels = [
    "True Positive (TP)",
    "False Positive (FP)",
    "True Negative (TN)",
    "False Negative (FN)"
]

values = np.array([
    14,     # TP
    66,     # FP
    35863,  # TN
    0       # FN
])

# IEEE-safe colors
colors = [
    "#2ca02c",  # TP - Green
    "#ff7f0e",  # FP - Orange
    "#1f77b4",  # TN - Blue
    "#d62728"   # FN - Red
]

# ----------------------------------
# PLOT (FINAL IEEE VERSION)
# ----------------------------------
plt.figure(figsize=(6, 6))

# Replace 0 with 1 only for plotting (log-scale safety)
plot_values = np.where(values == 0, 1, values)

bars = plt.bar(
    labels,
    plot_values,
    color=colors,
    width=0.55
)

# 🔑 KEY FIX: LOG SCALE
plt.yscale("log")

plt.ylabel("Number of Events (log scale)", fontsize=11)
plt.title(
    "Real-Time Intrusion Detection Performance of the Proposed System",
    fontsize=12
)

# IEEE grid
plt.grid(axis="y", linestyle="--", alpha=0.4)

# Value annotations (true values shown)
for bar, true_val in zip(bars, values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{true_val}",
        ha="center",
        va="bottom",
        fontsize=10
    )

# Dataset note (outside plot – no overlap)
plt.figtext(
    0.5, -0.08,
    "Dataset: CICIDS2018 | Real-Time Traffic | Evaluation Engine Log Analysis",
    ha="center",
    fontsize=9
)

plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "Fig5_Realtime_Confusion_LogScale.png"),
    dpi=300,
    bbox_inches="tight"
)
plt.close()

print("✅ Real-Time Confusion Bar Chart generated (ALL DATA VISIBLE).")
