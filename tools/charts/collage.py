import json
import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------------
# PATHS
# ----------------------------------
RESULTS_FILE = "results/offline_evaluation_v2.json"
OUTPUT_DIR = os.path.join("docs", "phase2_charts_ieee")
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

# ----------------------------------
# CREATE 2x2 GRID (TABLE STYLE)
# ----------------------------------
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
axes = axes.flatten()

metrics = [
    ("accuracy", "Accuracy (%)", "(a) Accuracy"),
    ("precision", "Precision (%)", "(b) Precision"),
    ("recall", "Recall (%)", "(c) Recall"),
    ("f1_score", "F1-Score (%)", "(d) F1-Score")
]

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
    ax.set_title(title, fontsize=11, pad=6)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_xlabel("Training Data Percentage (%)", fontsize=10)
    ax.set_ylim(0, 100)

    ax.set_xticks(train_x + bar_width * len(models) / 2)
    ax.set_xticklabels(train_labels, fontsize=9)

    # Grid
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    # Thick subplot borders (table cells)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)

    # Legend inside each subplot
    ax.legend(
        loc="lower center",
        fontsize=7,
        ncol=2,
        frameon=True,
        borderpad=0.3,
        handletextpad=0.4
    )

# ----------------------------------
# TABLE DIVIDER LINES
# ----------------------------------
# Vertical divider
fig.lines.append(
    plt.Line2D([0.5, 0.5], [0.10, 0.94],
               transform=fig.transFigure,
               linewidth=2.0,
               color="black")
)

# Horizontal divider
fig.lines.append(
    plt.Line2D([0.06, 0.95], [0.525, 0.525],  # ⬆️ moved UP
               transform=fig.transFigure,
               linewidth=2.0,
               color="black")
)


# Outer border
fig.patch.set_edgecolor("black")
fig.patch.set_linewidth(2.5)

# ----------------------------------
# DATASET NOTE (MOVED UP)
# ----------------------------------
fig.text(
    0.5,
    0.055,   # ⬆️ moved slightly upward
    "Dataset: CICIDS2018 | Train/Test Split: 80% / 20%",
    ha="center",
    fontsize=9
)

# ----------------------------------
# IMAGE TITLE / CAPTION (BOTTOM)
# ----------------------------------
fig.text(
    0.5,
    0.02,
    "Figure . Offline performance comparison of machine learning models",
    ha="center",
    fontsize=10,
    style="italic"
)

# Layout
plt.tight_layout(rect=[0.03, 0.10, 0.97, 0.95])

# ----------------------------------
# SAVE
# ----------------------------------
save_path = os.path.join(
    OUTPUT_DIR,
    "Fig_Offline_Performance_TableStyle_Collage1.png"
)
plt.savefig(save_path, dpi=300)
plt.close()

print(f"✅ Table-style collage saved at: {save_path}")