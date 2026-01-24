import os
import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# ================================
# PATH CONFIG
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_DIR = os.path.join(BASE_DIR, "..", "docs", "metrics")
FIGURES_DIR = os.path.join(BASE_DIR, "..", "docs", "charts")
os.makedirs(FIGURES_DIR, exist_ok=True)

# ================================
# LOAD METRICS
# ================================
metrics = defaultdict(lambda: defaultdict(dict))

for file in os.listdir(METRICS_DIR):
    if file.endswith(".json"):
        with open(os.path.join(METRICS_DIR, file)) as f:
            d = json.load(f)

        metrics[d["train_percentage"]][d["model"]] = {
            "accuracy": d["accuracy"] * 100,
            "precision": d["precision"] * 100,
            "recall": d["recall"] * 100,
            "f1": d["f1"] * 100
        }

train_pcts = sorted(metrics.keys())

MODEL_ORDER = [
    "LogisticRegression",
    "NaiveBayes",
    "SupportVectorMachine",
    "KNN",
    "DecisionTree",
    "RandomForest",
    "GradientBoosting",
    "XGBoost",
    "LightGBM",
    "MultiLayerPerceptron"
]

models = [m for m in MODEL_ORDER if any(m in metrics[p] for p in train_pcts)]

# ================================
# COLORS (CONSISTENT)
# ================================
colors = plt.cm.tab10.colors
bar_width = 0.7 / len(models)
x = np.arange(len(train_pcts))

# ================================
# CREATE 2x2 MULTI-PANEL FIGURE
# ================================
fig, axs = plt.subplots(2, 2, figsize=(14, 8))
axs = axs.flatten()

metric_list = [
    ("accuracy", "Accuracy (%)"),
    ("precision", "Precision (%)"),
    ("recall", "Recall (%)"),
    ("f1", "F1-Score (%)")
]

for ax, (metric_key, ylabel) in zip(axs, metric_list):
    for i, model in enumerate(models):
        values = [metrics[p][model][metric_key] for p in train_pcts]
        ax.bar(
            x + i * bar_width,
            values,
            bar_width,
            color=colors[i % len(colors)],
            label=model
        )

    ax.set_ylabel(ylabel)
    ax.set_xticks(x + bar_width * (len(models) - 1) / 2)
    ax.set_xticklabels(train_pcts)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

# ================================
# COMMON X LABEL
# ================================
for ax in axs[2:]:
    ax.set_xlabel("Training Percentage (%)")

# ================================
# GLOBAL LEGEND (LIKE TEACHER)
# ================================
fig.legend(
    models,
    loc="upper center",
    ncol=5,
    fontsize=9,
    frameon=True
)

fig.suptitle(
    "Comparative Performance Analysis of ML Models",
    fontsize=14,
    y=0.97
)

plt.tight_layout(rect=[0, 0, 1, 0.93])

# ================================
# SAVE FIGURE
# ================================
out_path = os.path.join(FIGURES_DIR, "Fig_IEEE_MultiPanel_Comparison.png")
plt.savefig(out_path, dpi=300)
plt.close()

print(f"✅ Teacher-style IEEE multi-panel figure saved: {out_path}")
