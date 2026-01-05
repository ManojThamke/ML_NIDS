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
FIGURES_DIR = os.path.join(BASE_DIR, "..", "docs", "chartI")

os.makedirs(FIGURES_DIR, exist_ok=True)

# ================================
# STORAGE
# ================================
metrics = defaultdict(lambda: defaultdict(dict))     # accuracy/precision/recall/f1
roc_auc_metrics = defaultdict(dict)                  # ONLY OFFLINE

# ================================
# LOAD METRICS (SAFE FOR REALTIME)
# ================================
for file in os.listdir(METRICS_DIR):
    if not file.endswith(".json"):
        continue

    with open(os.path.join(METRICS_DIR, file), "r") as f:
        data = json.load(f)

    model = data.get("model", "UnknownModel")

    # ----------------------------
    # OFFLINE METRICS (40/50/60/70)
    # ----------------------------
    if "train_percentage" in data:
        train_pct = data["train_percentage"]

        metrics[train_pct][model] = {
            "accuracy": data.get("accuracy", 0) * 100,
            "precision": data.get("precision", 0) * 100,
            "recall": data.get("recall", 0) * 100,
            "f1": data.get("f1", 0) * 100
        }

        if "roc_auc" in data:
            roc_auc_metrics[train_pct][model] = data["roc_auc"] * 100

    # ----------------------------
    # REALTIME METRICS (NO ROC-AUC)
    # ----------------------------
    else:
        train_pct = 70  # logical bucket (display only)

        metrics[train_pct][model] = {
            "accuracy": data.get("accuracy", 0) * 100,
            "precision": data.get("precision", 0) * 100,
            "recall": data.get("recall", 0) * 100,
            "f1": data.get("f1", 0) * 100
        }

train_percents = sorted(metrics.keys())

# ================================
# FIX MODEL ORDER (IEEE + VIVA SAFE)
# ================================
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

models = [m for m in MODEL_ORDER if any(m in metrics[p] for p in train_percents)]

# ================================
# IEEE SAFE COLORS
# ================================
COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
    "#bcbd22", "#17becf"
]

# ================================
# GENERIC BAR PLOT
# ================================
def plot_bar(metric_key, ylabel, title, filename):
    x = np.arange(len(train_percents))
    bar_width = 0.8 / len(models)

    plt.figure(figsize=(10, 4.5))

    for i, model in enumerate(models):
        values = [metrics[p].get(model, {}).get(metric_key, 0) for p in train_percents]
        plt.bar(
            x + i * bar_width,
            values,
            width=bar_width,
            color=COLORS[i],
            label=model
        )

    plt.xlabel("Training Data Percentage (%)", fontsize=11)
    plt.ylabel(ylabel, fontsize=11)
    plt.title(title, fontsize=12)

    plt.xticks(
        x + bar_width * (len(models) - 1) / 2,
        train_percents,
        fontsize=10
    )

    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 0.30),
        ncol=3,
        fontsize=8,
        frameon=True
    )

    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.margins(x=0.01)
    plt.tight_layout()

    path = os.path.join(FIGURES_DIR, filename)
    plt.savefig(path, dpi=300)
    plt.close()

    print(f"✅ Saved: {path}")

# ================================
# ROC–AUC BAR PLOT (OFFLINE ONLY)
# ================================
def plot_roc_auc_bar(title, filename):
    train_pcts = sorted(roc_auc_metrics.keys())
    if not train_pcts:
        print("⚠️ No ROC-AUC data found (offline only)")
        return

    models_roc = sorted({m for t in roc_auc_metrics.values() for m in t})
    x = np.arange(len(train_pcts))
    bar_width = 0.8 / len(models_roc)

    plt.figure(figsize=(10, 4.5))

    for i, model in enumerate(models_roc):
        values = [roc_auc_metrics[p].get(model, 0) for p in train_pcts]
        plt.bar(
            x + i * bar_width,
            values,
            width=bar_width,
            label=model
        )

    plt.xlabel("Training Data Percentage (%)", fontsize=11)
    plt.ylabel("ROC–AUC (%)", fontsize=11)
    plt.title(title, fontsize=12)

    plt.xticks(
        x + bar_width * (len(models_roc) - 1) / 2,
        train_pcts,
        fontsize=10
    )

    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 0.30),
        ncol=3,
        fontsize=8,
        frameon=True
    )

    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.margins(x=0.01)
    plt.tight_layout()

    path = os.path.join(FIGURES_DIR, filename)
    plt.savefig(path, dpi=300)
    plt.close()

    print(f"✅ Saved: {path}")

# ================================
# GENERATE ALL FIGURES
# ================================
plot_bar("accuracy", "Accuracy (%)",
         "Comparative Accuracy Analysis of ML Models",
         "Fig_Accuracy_Bar_IEEE.png")

plot_bar("precision", "Precision (%)",
         "Comparative Precision Analysis of ML Models",
         "Fig_Precision_Bar_IEEE.png")

plot_bar("recall", "Recall (%)",
         "Comparative Recall Analysis of ML Models",
         "Fig_Recall_Bar_IEEE.png")

plot_bar("f1", "F1-Score (%)",
         "Comparative F1-Score Analysis of ML Models",
         "Fig_F1_Bar_IEEE.png")

plot_roc_auc_bar(
    "Comparative ROC–AUC Analysis of ML Models",
    "Fig_ROC_AUC_Bar_IEEE.png"
)

print("\n🎉 ALL IEEE-STYLE CHARTS GENERATED SUCCESSFULLY")
