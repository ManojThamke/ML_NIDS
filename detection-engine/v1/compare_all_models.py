import os
import json
import math
from glob import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS_DIR = os.path.join(ROOT, "detection-engine", "models")
OUT_DIR = os.path.join(ROOT, "docs", "week4")
os.makedirs(OUT_DIR, exist_ok=True)

# pattern for metrics files (common names used earlier)
metrics_files = glob(os.path.join(MODELS_DIR, "*_metrics.json"))
# also allow plain metrics.json or model-specific names
metrics_files += glob(os.path.join(MODELS_DIR, "*metrics.json"))
metrics_files = sorted(set(metrics_files))

if not metrics_files:
    raise SystemExit(f"No metrics JSON files found in {MODELS_DIR}. Run model training scripts first.")

rows = []
for mf in metrics_files:
    name = os.path.basename(mf).replace("_metrics.json", "").replace("metrics.json", "")
    try:
        with open(mf, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as e:
        print("Warning: failed to load", mf, ":", e)
        continue

    # helper to grab nested report values if present
    def get_val(d, key):
        if key in d:
            return d[key]
        # try nested 'report' -> 'macro avg' or similar if requested (skip here)
        return None

    acc = get_val(data, "accuracy")
    prec = get_val(data, "precision")
    rec = get_val(data, "recall")
    f1 = get_val(data, "f1")
    roc = get_val(data, "roc_auc") or get_val(data, "roc_auc_score") or data.get("roc", None)

    train_time = data.get("train_time_seconds") or data.get("train_time") or data.get("training_time_seconds")
    infer_time = data.get("inference_time_seconds") or data.get("predict_time_seconds") or data.get("inference_time") or None

    # average predict ms per sample (preferred). If not present, compute from inference_time / n_test_samples
    avg_ms = data.get("avg_predict_ms_per_sample")
    if avg_ms is None and infer_time is not None:
        n_test = data.get("n_test_samples") or data.get("n_test") or data.get("n_test_samples_eval")
        try:
            if n_test:
                avg_ms = (float(infer_time) / float(n_test)) * 1000.0
            else:
                avg_ms = None
        except Exception:
            avg_ms = None

    # safe conversions
    def to_float(x):
        try:
            if x is None:
                return None
            return float(x)
        except Exception:
            return None

    rows.append({
        "model": name,
        "accuracy": to_float(acc),
        "precision": to_float(prec),
        "recall": to_float(rec),
        "f1": to_float(f1),
        "roc_auc": to_float(roc),
        "train_time_s": to_float(train_time),
        "inference_time_s": to_float(infer_time),
        "avg_predict_ms_per_sample": to_float(avg_ms),
        "metrics_file": os.path.relpath(mf, ROOT)
    })

# Build DataFrame and sort by f1 (desc)
df = pd.DataFrame(rows)
# normalize model names: replace hyphens/underscores with spaces capitalized
df["model_pretty"] = df["model"].str.replace("_", " ").str.replace("-", " ").str.title()
df = df.sort_values(by=["f1", "accuracy"], ascending=[False, False]).reset_index(drop=True)

# Save CSV
csv_out = os.path.join(OUT_DIR, "full_model_comparison.csv")
df.to_csv(csv_out, index=False)

# Write markdown summary
md_out = os.path.join(OUT_DIR, "full_model_comparison.md")
with open(md_out, "w", encoding="utf-8") as fh:
    fh.write("# Full Model Comparison\n\n")
    fh.write("Generated from model metrics in `detection-engine/models/`.\n\n")
    fh.write("## Table (sorted by F1 desc)\n\n")
    fh.write(df[[
        "model_pretty", "accuracy", "precision", "recall", "f1", "roc_auc",
        "train_time_s", "inference_time_s", "avg_predict_ms_per_sample"
    ]].to_markdown(index=False))
    fh.write("\n\n## Notes\n\n")
    fh.write("- `avg_predict_ms_per_sample` is preferred for inference speed comparison; when missing it's computed from inference_time_s / n_test_samples if n_test_samples is available in the JSON.\n")
    fh.write("- Missing values are shown as blank. If important metrics are missing, regenerate those model metric files with training scripts.\n")
    fh.write("\n\n## Raw files used:\n")
    for mf in metrics_files:
        fh.write(f"- `{os.path.relpath(mf, ROOT)}`\n")

print("Saved comparison CSV:", csv_out)
print("Saved markdown:", md_out)

# --- Plot 1: Accuracy and F1 side-by-side bar chart ---
plot_df = df.copy()

# DROP rows that have neither accuracy nor f1 (these cause empty tick slots)
plot_df = plot_df.dropna(subset=["accuracy", "f1"], how="all").reset_index(drop=True)

# ensure model_pretty is non-empty
plot_df["model_pretty"] = plot_df["model_pretty"].fillna("").replace("", "Unnamed Model")

# Limit to top N models (all)
plot_df = plot_df.sort_values(by="f1", ascending=False).reset_index(drop=True)
labels = plot_df["model_pretty"].tolist()
n = len(labels)
if n == 0:
    raise SystemExit("No models with metrics available to plot.")

x = list(range(n))

plt.figure(figsize=(max(8, n*0.6), 6))
width = 0.35
acc_vals = plot_df["accuracy"].fillna(0).tolist()
f1_vals = plot_df["f1"].fillna(0).tolist()

bars_acc = plt.bar([i - width/2 for i in x], acc_vals, width=width, label="Accuracy")
bars_f1  = plt.bar([i + width/2 for i in x], f1_vals,  width=width, label="F1-score")

plt.xticks(x, labels, rotation=45, ha="right")
plt.ylabel("Score")
plt.title("Model Comparison — Accuracy vs F1")
plt.legend()
plt.tight_layout()

# enforce tight x-limits so no left/right blank padding
plt.xlim(-0.5, n - 0.5)

# annotate bars with values when >0
for b, v in zip(list(bars_acc) + list(bars_f1), acc_vals + f1_vals):
    try:
        if v is not None and not math.isnan(v) and v > 0:
            plt.annotate(f"{v:.2f}", xy=(b.get_x() + b.get_width()/2, b.get_height()),
                         xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=8)
    except Exception:
        pass

img1 = os.path.join(OUT_DIR, "model_metrics_bar.png")
plt.savefig(img1, dpi=200)
plt.close()
print("Saved metrics bar chart:", img1)

# --- Plot 2: Inference speed (avg ms per sample) ---
# prefer avg_predict_ms_per_sample, fallback to inference_time_s (already computed earlier if possible)
speed_df = plot_df.copy()
speed_vals = []
for r in speed_df.to_dict(orient="records"):
    ms = r.get("avg_predict_ms_per_sample")
    if ms is None:
        # fallback: set NaN so it won't plot as 0 and distort bars
        speed_vals.append(float("nan"))
    else:
        speed_vals.append(float(ms))

plt.figure(figsize=(max(8, n*0.6), 5))
# replace NaN with 0 for plotting but we'll mask annotation for NaN
plot_vals = [0 if (v is None or (isinstance(v, float) and math.isnan(v))) else v for v in speed_vals]
bars = plt.bar(range(n), plot_vals)
plt.xticks(range(n), labels, rotation=45, ha="right")
plt.ylabel("Avg predict ms per sample (lower is faster)")
plt.title("Inference Speed Comparison (lower better)")
plt.tight_layout()

# annotate non-NaN speed bars
for idx, (b, v) in enumerate(zip(bars, speed_vals)):
    try:
        if v is not None and not (isinstance(v, float) and math.isnan(v)) and v > 0:
            plt.annotate(f"{v:.2f} ms", xy=(b.get_x() + b.get_width()/2, b.get_height()),
                         xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=8)
    except Exception:
        pass

img2 = os.path.join(OUT_DIR, "inference_speed_bar.png")
plt.savefig(img2, dpi=200)
plt.close()
print("Saved inference speed chart:", img2)

print("All done. Files written to:", OUT_DIR)
