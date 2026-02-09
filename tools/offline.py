import json
import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------------
# PATHS
# ----------------------------------
RESULTS_FILE = "results/offline_evaluation_v2.json"
OUTPUT_DIR = os.path.join("docs", "phase2_charts_ieee22")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "Fig_6_Offline_Performance_Collage.png"
)

# ----------------------------------
# LOAD RESULTS
# ----------------------------------
with open(RESULTS_FILE, "r") as f:
    results = json.load(f)

train_labels = ["40%", "50%", "60%", "70%", "80%", "90%", "100%"]
train_x = np.arange(len(train_labels))
models = list(results.keys())

bar_width = 0.07
colors = plt.get_cmap("tab10").colors

metrics = [
    ("accuracy", "Accuracy (%)", "a) Accuracy"),
    ("precision", "Precision (%)", "b) Precision"),
    ("recall", "Recall (%)", "c) Recall"),
    ("f1_score", "F1-Score (%)", "d) F1-Score"),
]

# ----------------------------------
# CREATE 2×2 COLLAGE
# ----------------------------------
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()

for ax, (metric_key, ylabel, title) in zip(axes, metrics):

    for i, model in enumerate(models):
        values = [results[model][p][metric_key] * 100 for p in train_labels]
        ax.bar(
            train_x + i * bar_width,
            values,
            bar_width,
            color=colors[i % len(colors)],
            label=model
        )

    # Titles & labels
    ax.set_title(title, fontsize=12, pad=8)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_xlabel("Training Data Percentage (%)", fontsize=10)
    ax.set_ylim(0, 100)

    ax.set_xticks(train_x + bar_width * len(models) / 2)
    ax.set_xticklabels(train_labels, fontsize=9)

    # Grid
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    # Legend (compact)
    ax.legend(
        loc="lower center",
        fontsize=7,
        ncol=3,
        frameon=True,
        borderpad=0.3,
        handletextpad=0.4
    )

    # Thicker borders (table look)
    for spine in ax.spines.values():
        spine.set_linewidth(1.3)

# ----------------------------------
# TABLE-STYLE DIVIDER LINES
# ----------------------------------
fig.lines.append(
    plt.Line2D([0.5, 0.5], [0.08, 0.95],
               transform=fig.transFigure,
               linewidth=2,
               color="black")
)

fig.lines.append(
    plt.Line2D([0.05, 0.95], [0.52, 0.52],
               transform=fig.transFigure,
               linewidth=2,
               color="black")
)

# Outer border
fig.patch.set_edgecolor("black")
fig.patch.set_linewidth(2.5)

# ----------------------------------
# FOOTNOTE + CAPTION
# ----------------------------------
fig.text(
    0.5,
    0.055,
    "Dataset: CICIDS2018 | Train/Test Split: 80% / 20%",
    ha="center",
    fontsize=9
)

fig.text(
    0.5,
    0.02,
    "Figure 6. Offline performance comparison of machine learning models",
    ha="center",
    fontsize=10,
    style="italic"
)

plt.tight_layout(rect=[0.03, 0.08, 0.97, 0.95])

# ----------------------------------
# SAVE
# ----------------------------------
plt.savefig(OUTPUT_FILE, dpi=300)
plt.close()

print(f"✅ Offline collage saved at: {OUTPUT_FILE}")
