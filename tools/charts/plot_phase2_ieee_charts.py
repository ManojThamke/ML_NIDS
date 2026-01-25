import json
import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------------
# Paths
# ----------------------------------
RESULTS_FILE = "results/offline_evaluation_v2.json"
OUTPUT_DIR = os.path.join("docs", "phase2_charts")

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

# ----------------------------------
# Generic plotting function
# ----------------------------------
def plot_metric(metric_key, ylabel, title, filename):
    plt.figure(figsize=(14, 6))
    bar_width = 0.08

    # Plot bars
    for i, model in enumerate(models):
        values = [
            results[model][p][metric_key] * 100
            for p in train_labels
        ]
        plt.bar(train_x + i * bar_width, values, bar_width, label=model)

    # Axis labels & title
    plt.xlabel("Training Percentage (%)", fontsize=11)
    plt.ylabel(ylabel, fontsize=11)
    plt.title(title, fontsize=12)
    plt.xticks(train_x + bar_width * len(models) / 2, train_labels)

    # Legend (centered)
    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 0.30),
        ncol=3,
        fontsize=9,
        frameon=True
    )

    # -------------------------------
    # Dataset information annotation
    # -------------------------------
    dataset_info = (
        "Dataset: CICIDS2018\n"
        "Total Samples: ~16.2M\n"
        "Train/Test Split: 80% / 20%\n"
        "Train: ~12.99M | Test: ~3.25M"
    )

    plt.text(
        0.70, 0.30,
        dataset_info,
        transform=plt.gca().transAxes,
        fontsize=9,
        verticalalignment="top",
        bbox=dict(
            boxstyle="round",
            facecolor="white",
            alpha=0.85
        )
    )

    # Grid & save
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()

    save_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Saved: {filename}")

# ----------------------------------
# Generate IEEE-style figures
# ----------------------------------
plot_metric(
    metric_key="accuracy",
    ylabel="Accuracy (%)",
    title="Comparative Accuracy Analysis of ML Models",
    filename="Fig1_Accuracy_IEEE.png"
)

plot_metric(
    metric_key="precision",
    ylabel="Precision (%)",
    title="Comparative Precision Analysis of ML Models",
    filename="Fig2_Precision_IEEE.png"
)

plot_metric(
    metric_key="recall",
    ylabel="Recall (%)",
    title="Comparative Recall Analysis of ML Models",
    filename="Fig3_Recall_IEEE.png"
)

plot_metric(
    metric_key="f1_score",
    ylabel="F1-Score (%)",
    title="Comparative F1-Score Analysis of ML Models",
    filename="Fig4_F1Score_IEEE.png"
)

plot_metric(
    metric_key="roc_auc",
    ylabel="ROC–AUC (%)",
    title="Comparative ROC–AUC Analysis of ML Models",
    filename="Fig5_ROCAUC_IEEE.png"
)

print("\n🎯 Phase-2.1 IEEE charts generated successfully.")
