import matplotlib.pyplot as plt
import os
import numpy as np

# ----------------------------------
# OUTPUT PATH
# ----------------------------------
OUTPUT_DIR = os.path.join("docs", "phase2_charts_ieee")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------
# MODEL DOMINANCE DATA (REAL-TIME)
# ----------------------------------
models = [
    "RandomForest",
    "GradientBoosting",
    "LightGBM",
    "DecisionTree",
    "MLP",
    "KNN",
    "XGBoost",
    "LogisticRegression",
    "NaiveBayes"
]

dominance_counts = np.array([
    22527,
    5020,
    4084,
    1843,
    1361,
    838,
    175,
    59,
    36
])

# IEEE-safe colors
colors = [
    "#1f77b4",  # RandomForest
    "#ff7f0e",
    "#2ca02c",
    "#9467bd",
    "#bcbd22",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#d62728"
]

# ----------------------------------
# PLOT (SCALABLE + IEEE READY)
# ----------------------------------
plt.figure(figsize=(6, 6))  # square & compact

bars = plt.barh(
    models,
    dominance_counts,
    color=colors
)

# LOG SCALE
plt.xscale("log")

# 🔑 FIX: Add padding so RF does not touch border
max_val = dominance_counts.max()
plt.xlim(left=30, right=max_val * 2.02)

plt.xlabel("Number of Dominant Predictions (log scale)", fontsize=11)
plt.title(
    "Scalable Real-Time Model Dominance in Ensemble Detection",
    fontsize=12
)

# Strongest model on top
plt.gca().invert_yaxis()

# Grid (IEEE style)
plt.grid(axis="x", linestyle="--", alpha=0.4)

# 🔑 FIX: Shift annotation slightly right
for bar, value in zip(bars, dominance_counts):
    plt.annotate(
        f"{int(value)}",
        xy=(value, bar.get_y() + bar.get_height() / 2),
        xytext=(1, 0),                 # shift right by 6 points
        textcoords="offset points",
        va="center",
        fontsize=9,
        clip_on=False                 # 🔑 prevent clipping
    )


# Dataset note (outside plot – IEEE safe)
plt.figtext(
    0.5, -0.08,
    "Dataset: CICIDS2018 | Real-Time Traffic | Evaluation Engine Analysis",
    ha="center",
    fontsize=9
)

plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "Fig6_Realtime_Model_Dominance_LogScale.png"),
    dpi=300,
    bbox_inches="tight"
)
plt.close()

print("✅ Scalable Model Dominance chart generated (FINAL & IEEE READY).")
