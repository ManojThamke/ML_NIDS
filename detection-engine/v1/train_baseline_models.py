# detection-engine/train_baseline_models.py
"""
Day 17 — Train baseline models (Logistic Regression + Decision Tree)
Outputs:
 - detection-engine/models/logreg_baseline.pkl
 - detection-engine/models/decisiontree_baseline.pkl
 - detection-engine/models/baseline_metrics.json
 - docs/model_results.md
 - docs/baseline_comparison.png (bar chart)
"""
import os, json, joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix, classification_report)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_IN = os.path.join(ROOT, "data", "preprocessed_train.csv")
OUT_DIR = os.path.join(os.path.dirname(__file__), "models")
DOCS_DIR = os.path.join(ROOT, "docs")
METRICS_JSON = os.path.join(OUT_DIR, "baseline_metrics.json")
DOCS_MD = os.path.join(DOCS_DIR, "model_results.md")
PLOT_PATH = os.path.join(DOCS_DIR, "baseline_comparison.png")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

print("Loading preprocessed data:", DATA_IN)
df = pd.read_csv(DATA_IN)

if "Label" not in df.columns:
    raise SystemExit("Label column not found in preprocessed data.")

X = df.drop(columns=["Label"])
y = df["Label"].astype(int)

# Train/test split (70/30)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

models = {
    "LogisticRegression": LogisticRegression(max_iter=1000, solver="liblinear"),
    "DecisionTree": DecisionTreeClassifier(random_state=42)
}

results = {}

for name, model in models.items():
    print(f"\nTraining {name} ...")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    try:
        y_prob = model.predict_proba(X_test)[:, 1]
    except Exception:
        y_prob = None

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc = float(roc_auc_score(y_test, y_prob)) if y_prob is not None else None
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, output_dict=True)

    results[name] = {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "roc_auc": roc,
        "confusion_matrix": cm,
        "report": report
    }

    # Save model
    model_path = os.path.join(OUT_DIR, f"{name.lower()}_baseline.pkl")
    joblib.dump({"model": model, "feature_columns": X.columns.tolist()}, model_path)
    print(f"Saved model to: {model_path}")

# Save metrics JSON
with open(METRICS_JSON, "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=2)
print("\nMetrics saved to:", METRICS_JSON)

# Write summary MD
with open(DOCS_MD, "w", encoding="utf-8") as fh:
    fh.write("# Baseline Model Results — Day 17\n\n")
    fh.write("Trained models: Logistic Regression, Decision Tree\n\n")
    for name, stats in results.items():
        fh.write(f"## {name}\n\n")
        fh.write(f"- Accuracy: {stats['accuracy']:.4f}\n")
        fh.write(f"- Precision: {stats['precision']:.4f}\n")
        fh.write(f"- Recall: {stats['recall']:.4f}\n")
        fh.write(f"- F1-score: {stats['f1']:.4f}\n")
        fh.write(f"- ROC-AUC: {stats['roc_auc'] if stats['roc_auc'] is not None else 'N/A'}\n\n")
        fh.write("Confusion matrix:\n\n")
        fh.write(str(stats["confusion_matrix"]) + "\n\n")
        fh.write("Short pros / cons:\n\n")
        if name == "LogisticRegression":
            fh.write("- Pros: fast, interpretable, stable baseline.\n")
            fh.write("- Cons: weak on non-linear patterns.\n\n")
        elif name == "DecisionTree":
            fh.write("- Pros: interpretable, captures non-linear interactions.\n")
            fh.write("- Cons: prone to overfitting.\n\n")
    fh.write("---\n\n")
    fh.write("Notes: These are baselines. Next step: ensemble models (RF, GBM, etc.)\n")
print("Wrote summary to:", DOCS_MD)

# Generate comparison plot
metrics_for_plot = ["accuracy", "f1"]
bar_data = {name: [stats[m] for m in metrics_for_plot] for name, stats in results.items()}

labels = list(bar_data.keys())
x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots()
ax.bar(x - width/2, [bar_data[l][0] for l in labels], width, label="Accuracy")
ax.bar(x + width/2, [bar_data[l][1] for l in labels], width, label="F1-score")

ax.set_ylabel("Score")
ax.set_title("Baseline Models Comparison (Day 17)")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

plt.tight_layout()
plt.savefig(PLOT_PATH)
plt.close()
print("Saved comparison plot to:", PLOT_PATH)

print("\nDay 17 complete ✅")
