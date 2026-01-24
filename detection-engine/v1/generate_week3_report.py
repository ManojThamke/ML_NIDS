"""
Day 21 — Generate Week 3 Report
Saves: docs/week3/week3_report.md
"""

import os, json
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DOCS_DIR = os.path.join(ROOT, "docs", "week3")
OUT_MD = os.path.join(DOCS_DIR, "week3_report.md")

# metric container files
containers = {
    "baseline": os.path.join(MODELS_DIR, "baseline_metrics.json"),
    "ensemble": os.path.join(MODELS_DIR, "ensemble_metrics.json"),
    "advanced": os.path.join(MODELS_DIR, "advanced_metrics.json"),
}

def try_float(x):
    try:
        return float(x) if x is not None else None
    except:
        return None

def load_json_safe(path):
    if not os.path.exists(path):
        return {}
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except Exception:
        return {}

results = {}
for name, path in containers.items():
    data = load_json_safe(path)
    if not data:
        continue
    for k, v in data.items():
        results[k] = {
            "container": name,
            "accuracy": try_float(v.get("accuracy")),
            "precision": try_float(v.get("precision")),
            "recall": try_float(v.get("recall")),
            "f1": try_float(v.get("f1")),
            "train_time": try_float(v.get("train_time_seconds") or v.get("train_time")),
        }

df = pd.DataFrame([
    {"model": k, **v} for k, v in results.items()
]) if results else pd.DataFrame()

if not df.empty:
    df_sorted = df.sort_values(by=["f1","recall","accuracy"], ascending=[False,False,False])
    top_k = df_sorted.head(3)
else:
    df_sorted = pd.DataFrame()
    top_k = pd.DataFrame()

# Ensure output dir exists
os.makedirs(DOCS_DIR, exist_ok=True)

with open(OUT_MD, "w", encoding="utf-8") as fh:
    fh.write("# Week 3 Report — ML_NIDS Project\n\n")
    fh.write("## ✅ Dataset + Pipeline Review\n")
    fh.write("- Final dataset created and preprocessed.\n")
    fh.write("- Feature engineering with 6–8 common features.\n")
    fh.write("- Models trained: Logistic Regression, Decision Tree, RF, GBM, XGB, LGBM.\n\n")

    fh.write("## 📊 Model Metrics\n")
    if df_sorted.empty:
        fh.write("No metrics found. Please rerun training scripts.\n")
    else:
        fh.write(df_sorted.to_markdown(index=False))
        fh.write("\n\n")

    fh.write("## 🏆 Top Candidates\n")
    if not top_k.empty:
        for _, row in top_k.iterrows():
            fh.write(f"- **{row['model']}** — F1={row['f1']:.4f}, Recall={row['recall']:.4f}, Acc={row['accuracy']:.4f}\n")
    else:
        fh.write("No candidates ranked.\n")

    fh.write("\n## 📌 Next Steps (Week 4 Plan)\n")
    fh.write("- Train remaining 5 models (SVM, KNN, Naive Bayes, MLP, Hybrid Ensemble).\n")
    fh.write("- Compare against Week 3 models.\n")
    fh.write("- Finalize top 3 for deployment.\n")

print("✅ Week 3 report generated at:", OUT_MD)
