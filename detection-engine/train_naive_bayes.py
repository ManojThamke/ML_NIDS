import os, json, joblib, time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, classification_report
)

# Paths
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_IN = os.path.join(ROOT, "data", "preprocessed_train.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DOCS_DIR = os.path.join(ROOT, "docs", "week4")
MODEL_OUT = os.path.join(MODELS_DIR, "naive_bayes.pkl")
METRICS_OUT = os.path.join(MODELS_DIR, "naive_bayes_metrics.json")
MD_OUT = os.path.join(DOCS_DIR, "day24_naive_bayes.md")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

print("Loading dataset:", DATA_IN)
df = pd.read_csv(DATA_IN)
if "Label" not in df.columns:
    raise SystemExit("Label column not found in preprocessed data.")

X = df.drop(columns=["Label"])
y = df["Label"].astype(int)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Train GaussianNB
print("Training GaussianNB...")
nb = GaussianNB()
t0 = time.time()
nb.fit(X_train, y_train)
train_time = time.time() - t0

# Evaluate
y_pred = nb.predict(X_test)
try:
    y_prob = nb.predict_proba(X_test)[:,1]
except Exception:
    y_prob = None

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, zero_division=0)
rec = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
roc = float(roc_auc_score(y_test, y_prob)) if y_prob is not None else None
cm = confusion_matrix(y_test, y_pred).tolist()
report = classification_report(y_test, y_pred, output_dict=True)

metrics = {
    "accuracy": float(acc),
    "precision": float(prec),
    "recall": float(rec),
    "f1": float(f1),
    "roc_auc": roc,
    "confusion_matrix": cm,
    "report": report,
    "train_time_seconds": train_time,
    "n_train_samples": len(X_train),
    "n_test_samples": len(X_test)
}

# Save model + metrics
joblib.dump({"model": nb, "feature_columns": X.columns.tolist()}, MODEL_OUT)
with open(METRICS_OUT, "w", encoding="utf-8") as fh:
    json.dump(metrics, fh, indent=2)

# Markdown summary
with open(MD_OUT, "w", encoding="utf-8") as fh:
    fh.write("# Day 24 — Naïve Bayes Results\n\n")
    fh.write(f"Model saved: `{os.path.relpath(MODEL_OUT, ROOT)}`\n\n")
    fh.write("## Metrics (on test set)\n\n")
    fh.write(f"- Accuracy: {acc:.4f}\n")
    fh.write(f"- Precision: {prec:.4f}\n")
    fh.write(f"- Recall: {rec:.4f}\n")
    fh.write(f"- F1-score: {f1:.4f}\n")
    fh.write(f"- ROC-AUC: {roc if roc is not None else 'N/A'}\n\n")
    fh.write("Confusion matrix:\n\n")
    fh.write(str(cm) + "\n\n")
    fh.write("Notes:\n- GaussianNB is extremely fast (training in <1s).\n")
    fh.write("- Works best with normally-distributed features.\n")
    fh.write("- Usually a weaker baseline vs. tree/boosting models.\n")

print("✅ Saved model, metrics, and report.")
print("\nDay 24 complete ✅")
