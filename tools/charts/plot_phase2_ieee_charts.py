import json
import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------------
# Paths
# ----------------------------------
RESULTS_FILE = "results/offline_evaluation_v2.json"
OUTPUT_DIR = os.path.join("docs", "phase2_charts_ieee")

os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"📁 Charts will be saved in: {os.path.abspath(OUTPUT_DIR)}")

# ----------------------------------
# Load results
# ----------------------------------
with open(RESULTS_FILE, "r") as f:
    results = json.load(f)

# Training percentages
train_labels = ["40%", "50%", "60%", "70%", "80%", "90%", "100%"]
train_x = np.arange(len(train_labels))

models = list(results.keys())

# Compact bar width
bar_width = 0.07

# IEEE-safe color palette
colors = plt.get_cmap("tab10").colors

# ----------------------------------
# Plot function (COMPACT + IEEE SAFE)
# ----------------------------------
def plot_metric(metric_key, ylabel, title, filename):
    plt.figure(figsize=(6, 4))  # ✅ SQUARE / COMPACT

    for i, model in enumerate(models):
        values = [results[model][p][metric_key] * 100 for p in train_labels]
        plt.bar(
            train_x + i * bar_width,
            values,
            bar_width,
            color=colors[i % len(colors)],
            label=model
        )

    # Labels & title
    plt.xlabel("Training Data Percentage (%)", fontsize=10)
    plt.ylabel(ylabel, fontsize=10)
    plt.title(title, fontsize=11)

    plt.xticks(
        train_x + bar_width * len(models) / 2,
        train_labels,
        fontsize=9
    )

    # Legend (compact, top-center)
    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.50, 0.30),
        ncol=3,
        fontsize=7,
        frameon=True
    )

    # Light grid (IEEE style)
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    # Dataset note (small, bottom-right)
    plt.figtext(
        0.95, 0.88,
        "Dataset: CICIDS2018 | Train/Test: 80/20",
        ha="right",
        va="bottom",
        fontsize=8
    )

    # Tight layout with reserved legend space
    plt.tight_layout(rect=[0, 0.05, 1, 0.90])

    save_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"✅ Saved: {filename}")

# ----------------------------------
# Generate charts
# ----------------------------------

plot_metric(
    metric_key="accuracy",
    ylabel="Accuracy (%)",
    title="Offline Accuracy Comparison Across Training Sizes",
    filename="Fig1_Offline_Accuracy.png"
)

plot_metric(
    metric_key="precision",
    ylabel="Precision (%)",
    title="Offline Precision Comparison Across Training Sizes",
    filename="Fig2_Offline_Precision.png"
)

plot_metric(
    metric_key="recall",
    ylabel="Recall (%)",
    title="Offline Recall Comparison Across Training Sizes",
    filename="Fig3_Offline_Recall.png"
)

# ✅ MAIN OFFLINE FIGURE (THIS ONE GOES IN PAPER)
plot_metric(
    metric_key="f1_score",
    ylabel="F1-Score (%)",
    title="Offline F1-Score Comparison of ML Models Across Training Sizes",
    filename="Fig4_Offline_F1Score.png"
)

plot_metric(
    metric_key="roc_auc",
    ylabel="ROC–AUC (%)",
    title="Offline ROC–AUC Comparison Across Training Sizes",
    filename="Fig5_Offline_ROCAUC.png"
)

print("\n🎯 All offline evaluation charts generated (COMPACT & IEEE READY).")
