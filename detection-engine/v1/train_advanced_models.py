import os, json, joblib, time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix, classification_report)

# model imports
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_IN = os.path.join(ROOT, "data", "preprocessed_train.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DOCS_DIR = os.path.join(ROOT, "docs")
METRICS_JSON = os.path.join(MODELS_DIR, "advanced_metrics.json")
MD_PATH = os.path.join(DOCS_DIR, "advanced_model_results.md")
PLOT_PATH = os.path.join(DOCS_DIR, "advanced_comparison.png")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

print("Loading preprocessed data:", DATA_IN)
df = pd.read_csv(DATA_IN)
if "Label" not in df.columns:
    raise SystemExit("Label column not found in preprocessed data.")

X = df.drop(columns=["Label"])
y = df["Label"].astype(int)

# train/test split (70/30)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# small search spaces for quick runs — you can expand later
xgb_param_dist = {
    "n_estimators": [50, 100, 200],
    "max_depth": [3, 6, 9],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.6, 0.8, 1.0],
    "colsample_bytree": [0.6, 0.8, 1.0]
}

lgbm_param_dist = {
    "n_estimators": [50, 100, 200],
    "num_leaves": [31, 63, 127],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.6, 0.8, 1.0],
    "colsample_bytree": [0.6, 0.8, 1.0]
}

# wrappers
xgb = XGBClassifier(use_label_encoder=False, eval_metric="logloss", n_jobs=-1, random_state=42)
lgbm = LGBMClassifier(n_jobs=-1, random_state=42)

# RandomizedSearchCV settings (small budget)
n_iter = 6
cv = 3
rs_kwargs = {"n_iter": n_iter, "cv": cv, "scoring": "f1", "n_jobs": 1, "random_state": 42, "verbose": 1}

results = {}

# Helper function to train + evaluate
def train_and_eval(model, param_dist, name):
    print(f"\n=== Training {name} (Randomized search {n_iter} iters, cv={cv}) ===")
    rs = RandomizedSearchCV(model, param_distributions=param_dist, **rs_kwargs)
    t0 = time.time()
    rs.fit(X_train, y_train)
    train_time = time.time() - t0
    best = rs.best_estimator_
    print(f"{name} best params:", rs.best_params_)
    # evaluate
    t0 = time.time()
    y_pred = best.predict(X_test)
    infer_time = time.time() - t0
    try:
        y_prob = best.predict_proba(X_test)[:,1]
    except Exception:
        y_prob = None
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc = float(roc_auc_score(y_test, y_prob)) if y_prob is not None else None
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, output_dict=True)

    # save model bundle
    model_path = os.path.join(MODELS_DIR, f"{name.lower()}_advanced.pkl")
    joblib.dump({"model": best, "feature_columns": X.columns.tolist()}, model_path)

    metrics = {
        "best_params": rs.best_params_,
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "roc_auc": roc,
        "confusion_matrix": cm,
        "report": report,
        "train_time_seconds": train_time,
        "inference_time_seconds": infer_time,
        "model_path": model_path
    }
    print(f"{name} done. acc={acc:.4f} f1={f1:.4f} train_s={train_time:.2f}")
    return metrics

# Train XGBoost
metrics_xgb = train_and_eval(xgb, xgb_param_dist, "XGBoost")
results["XGBoost"] = metrics_xgb

# Train LightGBM
metrics_lgbm = train_and_eval(lgbm, lgbm_param_dist, "LightGBM")
results["LightGBM"] = metrics_lgbm

# Save results
with open(METRICS_JSON, "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=2)
print("Saved advanced metrics to:", METRICS_JSON)

# Write docs summary
with open(MD_PATH, "w", encoding="utf-8") as fh:
    fh.write("# Advanced Models — Day 19\n\n")
    fh.write("Trained: XGBoost, LightGBM (basic randomized hyperparameter tuning)\n\n")
    for name, stats in results.items():
        fh.write(f"## {name}\n\n")
        fh.write(f"- Best params: {stats['best_params']}\n")
        fh.write(f"- Accuracy: {stats['accuracy']:.4f}\n")
        fh.write(f"- Precision: {stats['precision']:.4f}\n")
        fh.write(f"- Recall: {stats['recall']:.4f}\n")
        fh.write(f"- F1-score: {stats['f1']:.4f}\n")
        fh.write(f"- ROC-AUC: {stats['roc_auc'] if stats['roc_auc'] is not None else 'N/A'}\n")
        fh.write(f"- Train time (s): {stats['train_time_seconds']:.2f}\n")
        fh.write(f"- Inference time (s): {stats['inference_time_seconds']:.4f}\n\n")
        fh.write("Confusion matrix:\n")
        fh.write(str(stats["confusion_matrix"]) + "\n\n")
    fh.write("---\n\n")
    fh.write("Notes: This was a small-budget tuning run (n_iter=6). Increase n_iter and search ranges for better tuning.\n")
print("Wrote advanced summary to:", MD_PATH)

# Plot comparison (Accuracy & F1)
labels = list(results.keys())
accs = [results[k]["accuracy"] for k in labels]
f1s = [results[k]["f1"] for k in labels]
train_times = [results[k]["train_time_seconds"] for k in labels]

x = np.arange(len(labels))
width = 0.35
fig, ax = plt.subplots(figsize=(7,4))
ax.bar(x - width/2, accs, width, label="Accuracy")
ax.bar(x + width/2, f1s, width, label="F1")
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylim(0,1.05)
ax.set_ylabel("Score")
ax.legend(loc="upper left")

# secondary axis for train times
ax2 = ax.twinx()
ax2.plot(x, train_times, color="black", marker="o", linestyle="--", label="Train time (s)")
ax2.set_ylabel("Train time (s)")
ax2.legend(loc="upper right")

plt.title("Advanced Models Comparison (Day 19)")
plt.tight_layout()
plt.savefig(PLOT_PATH)
plt.close()
print("Saved comparison plot to:", PLOT_PATH)

print("\nDay 19 complete ✅")
