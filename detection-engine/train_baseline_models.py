import os, json, joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix, classification_report)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_IN = os.path.join(ROOT, "data", "preprocessed_train.csv")
OUT_DIR = os.path.join(os.path.dirname(__file__), "models")
METRICS_JSON = os.path.join(OUT_DIR, "baseline_metrics.json")
DOCS_MD = os.path.join(ROOT, "docs", "model_results.md")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DOCS_MD), exist_ok=True)

print("Loading preprocessed data:", DATA_IN)
df = pd.read_csv(DATA_IN)

if "Label" not in df.columns:
    raise SystemExit("Label column not found in preprocessed data.")

X = df.drop(columns=["Label"])
y = df["Label"].astype(int)

# Train/test split (70/30) with stratify
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

    # Predictions & probs
    y_pred = model.predict(X_test)
    try:
        y_prob = model.predict_proba(X_test)[:, 1]
    except Exception:
        # If no predict_proba, use decision_function (scaled) if available
        if hasattr(model, "decision_function"):
            scores = model.decision_function(X_test)
            # attempt to map to (0,1) via min-max for ROC only (not ideal)
            y_prob = (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)
        else:
            y_prob = None

    # Metrics
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

    # Save model bundle (model only; preprocessing bundle saved in Day16)
    model_path = os.path.join(OUT_DIR, f"{name.lower()}_baseline.pkl")
    joblib.dump({"model": model, "feature_columns": X.columns.tolist()}, model_path)
    print(f"Saved model to: {model_path}")

# Persist metrics JSON
with open(METRICS_JSON, "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=2)

print("\nMetrics saved to:", METRICS_JSON)

# Create docs summary
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
            fh.write("- Pros: fast, interpretable coefficients, good baseline for linear separability.\n")
            fh.write("- Cons: limited if features are not linearly separable; sensitive to collinearity.\n\n")
        elif name == "DecisionTree":
            fh.write("- Pros: interpretable rules, captures non-linear interactions, no scaling required.\n")
            fh.write("- Cons: prone to overfitting; unstable to small data changes.\n\n")
    fh.write("---\n\n")
    fh.write("Notes:\n- These are baseline models. Next step: train stronger ensemble models (RF, XGB, LGBM) and compare.\n")

print("Wrote summary to:", DOCS_MD)
print("\nDay 17 complete.")
