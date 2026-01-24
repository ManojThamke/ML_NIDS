# detection-engine/compare_models_part1.py
"""
Day 20 — Model Comparison (Part 1)
Reads metrics JSONs saved by previous training scripts and produces:
 - docs/model_comparison_part1.md
 - docs/model_comparison_acc_f1.png
 - docs/model_comparison_speed.png
"""

import os, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DOCS_DIR = os.path.join(ROOT, "docs")
OUT_MD = os.path.join(DOCS_DIR, "model_comparison_part1.md")
PLOT_ACC_F1 = os.path.join(DOCS_DIR, "model_comparison_acc_f1.png")
PLOT_SPEED = os.path.join(DOCS_DIR, "model_comparison_speed.png")

os.makedirs(DOCS_DIR, exist_ok=True)

# Known metrics files we may have produced previously
metrics_files = {
    "baseline": os.path.join(MODELS_DIR, "baseline_metrics.json"),
    "ensemble": os.path.join(MODELS_DIR, "ensemble_metrics.json"),
    "advanced": os.path.join(MODELS_DIR, "advanced_metrics.json")
}

# target models we want to show (friendly names -> keys inside metric files)
# entries are (friendly name, container key(s) to look up)
target_list = [
    ("LogisticRegression", ("baseline", "LogisticRegression")),
    ("DecisionTree", ("baseline", "DecisionTree")),
    ("RandomForest", ("ensemble", "RandomForest")),
    ("GBM", ("ensemble", "GBM")),              # sklearn GBM
    ("XGBoost", ("advanced", "XGBoost")),
    ("LightGBM", ("advanced", "LightGBM"))
]

# helper to load metrics from container files
def load_container(path):
    if not os.path.exists(path):
        return {}
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except Exception:
        return {}

containers = {k: load_container(p) for k,p in metrics_files.items()}

rows = []
for friendly, (container_key, model_key) in target_list:
    container = containers.get(container_key, {})
    # handle when model_key may be absent or different naming: try fuzzy fallback
    metrics = {}
    if isinstance(container, dict) and model_key in container:
        metrics = container[model_key]
    else:
        # try to find a model in container with matching lowercase key
        found = None
        for k in container.keys():
            if k.lower().startswith(model_key.lower()):
                found = container[k]
                break
        if found:
            metrics = found
        else:
            metrics = None

    if not metrics:
        # skip missing model but mark as not available
        rows.append({
            "model": friendly,
            "accuracy": None,
            "precision": None,
            "recall": None,
            "f1": None,
            "train_time": None,
            "note": f"metrics missing ({container_key})"
        })
        continue

    # metrics may have different keys depending on script — normalize access safely
    acc = metrics.get("accuracy") or metrics.get("acc") or metrics.get("accuracy_score")
    prec = metrics.get("precision")
    rec = metrics.get("recall")
    f1 = metrics.get("f1")
    # train_time or train_time_seconds or train_time_seconds
    train_time = metrics.get("train_time") or metrics.get("train_time_seconds") or metrics.get("train_time_sec") or None

    # attempt to convert nested values to float safely
    def safe_float(x):
        try:
            return float(x)
        except Exception:
            return None

    rows.append({
        "model": friendly,
        "accuracy": safe_float(acc),
        "precision": safe_float(prec),
        "recall": safe_float(rec),
        "f1": safe_float(f1),
        "train_time": safe_float(train_time),
        "note": ""
    })

df = pd.DataFrame(rows)

# Save markdown summary table
with open(OUT_MD, "w", encoding="utf-8") as fh:
    fh.write("# Model Comparison — Part 1 (Day 20)\n\n")
    fh.write("This table aggregates available metrics (Accuracy, Precision, Recall, F1, Train time). Missing entries mean the training script did not produce metrics or file is not present.\n\n")
    fh.write(df.to_markdown(index=False))
    fh.write("\n\n**Notes**:\n- Accuracy can be misleading on imbalanced datasets; focus on Recall / Precision / F1 for attack detection.\n- Train time measured as wall-clock seconds during training run (may vary by machine).\n")
print("Wrote comparison markdown to:", OUT_MD)

# Prepare plots — filter only models with numeric metrics
plot_df = df.dropna(subset=["accuracy", "f1"]).reset_index(drop=True)
if not plot_df.empty:
    labels = plot_df["model"].tolist()
    accs = plot_df["accuracy"].tolist()
    f1s = plot_df["f1"].tolist()

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8,4))
    ax.bar(x - width/2, accs, width, label="Accuracy")
    ax.bar(x + width/2, f1s, width, label="F1-score")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0,1.05)
    ax.set_ylabel("Score")
    ax.set_title("Model Comparison — Accuracy vs F1")
    ax.legend()
    plt.tight_layout()
    plt.savefig(PLOT_ACC_F1)
    plt.close()
    print("Saved ACC/F1 plot to:", PLOT_ACC_F1)
else:
    print("Skipping ACC/F1 plot (no numeric metrics available).")

# Plot train times (if present)
time_df = df.dropna(subset=["train_time"]).reset_index(drop=True)
if not time_df.empty:
    labels = time_df["model"].tolist()
    times = time_df["train_time"].tolist()
    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(8,4))
    ax.bar(x, times, width=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Train time (s)")
    ax.set_title("Model Training Time (seconds)")
    plt.tight_layout()
    plt.savefig(PLOT_SPEED)
    plt.close()
    print("Saved train time plot to:", PLOT_SPEED)
else:
    print("Skipping train time plot (no train_time data).")

print("\nDay 20 comparison complete.")
