import os
import json
import matplotlib.pyplot as plt
from collections import defaultdict

# ================================
# PATH CONFIG
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_DIR = os.path.join(BASE_DIR, "..", "docs", "metrics")
FIGURES_DIR = os.path.join(BASE_DIR, "..", "docs", "figures")

os.makedirs(FIGURES_DIR, exist_ok=True)

# ================================
# LOAD METRICS
# ================================
metrics_data = defaultdict(dict)

for file in os.listdir(METRICS_DIR):
    if file.endswith(".json"):
        path = os.path.join(METRICS_DIR, file)
        with open(path, "r") as f:
            data = json.load(f)

        model = data["model"]
        train_pct = data["train_percentage"]

        metrics_data[model][train_pct] = {
            "accuracy": data["accuracy"] * 100,
            "precision": data["precision"] * 100,
            "recall": data["recall"] * 100,
            "f1": data["f1"] * 100
        }

# ================================
# IEEE PLOT FUNCTION
# ================================
def plot_metric(metric_key, ylabel, title, filename):
    plt.figure(figsize=(8, 4))

    for model, values in metrics_data.items():
        x = sorted(values.keys())
        y = [values[p][metric_key] for p in x]
        plt.plot(x, y, marker="o", linewidth=2, label=model)

    plt.xlabel("Training Data Percentage (%)", fontsize=10)
    plt.ylabel(ylabel, fontsize=10)
    plt.title(title, fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=8)
    plt.tight_layout()

    save_path = os.path.join(FIGURES_DIR, filename)
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"✅ Saved: {save_path}")

# ================================
# GENERATE IEEE FIGURES
# ================================
plot_metric(
    "accuracy",
    "Accuracy (%)",
    "Accuracy vs Training Data Percentage",
    "Fig_Accuracy_IEEE.png"
)

plot_metric(
    "precision",
    "Precision (%)",
    "Precision vs Training Data Percentage",
    "Fig_Precision_IEEE.png"
)

plot_metric(
    "recall",
    "Recall (%)",
    "Recall vs Training Data Percentage",
    "Fig_Recall_IEEE.png"
)

plot_metric(
    "f1",
    "F1-Score (%)",
    "F1-Score vs Training Data Percentage",
    "Fig_F1_IEEE.png"
)

print("\n🎉 IEEE-STYLE CHART GENERATION COMPLETED")
