import os
import json
import time
import argparse
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix, classification_report)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_IN = os.path.join(ROOT, "data", "preprocessed_train.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DOCS_DIR = os.path.join(ROOT, "docs", "week4")
MODEL_OUT = os.path.join(MODELS_DIR, "mlp.pkl")
METRICS_OUT = os.path.join(MODELS_DIR, "mlp_metrics.json")
MD_OUT = os.path.join(DOCS_DIR, "day25_mlp.md")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument("--sample", type=int, default=50000,
                    help="Stratified subsample size (default 50000). Use 0 or omit for full dataset (not recommended).")
parser.add_argument("--n_jobs", type=int, default=1, help="n_jobs for GridSearchCV (default 1)")
parser.add_argument("--grid", choices=["small", "full", "auto"], default="auto",
                    help="Hyperparameter grid size. 'auto' reduces when sample large.")
parser.add_argument("--max_iter", type=int, default=200, help="Max iterations for MLP (default 200)")
parser.add_argument("--verbose", type=int, default=1, help="GridSearchCV verbose")
args = parser.parse_args()

print("Loading dataset:", DATA_IN)
df = pd.read_csv(DATA_IN)
if "Label" not in df.columns:
    raise SystemExit("Label column 'Label' not found in preprocessed data.")

# handle sample=0 as full dataset
sample_size = args.sample
if sample_size is None or sample_size == 0 or sample_size >= len(df):
    print(f"Using full dataset (rows = {len(df)}).")
else:
    print(f"Dataset rows: {len(df)}. Subsampling to {sample_size} (stratified).")
    # stratified per-class sampling (robust)
    classes = df["Label"].unique()
    parts = []
    total = len(df)
    for cls in classes:
        cls_df = df[df["Label"] == cls]
        prop = len(cls_df) / total
        n_cls = max(1, int(round(sample_size * prop)))
        n_cls = min(n_cls, len(cls_df))
        parts.append(cls_df.sample(n=n_cls, random_state=42))
    df_small = pd.concat(parts, axis=0).reset_index(drop=True)
    # top-up if needed
    if len(df_small) < sample_size:
        remaining = sample_size - len(df_small)
        pool = df.drop(index=df_small.index, errors="ignore")
        if len(pool) >= remaining:
            df_small = pd.concat([df_small, pool.sample(n=remaining, random_state=42)], axis=0).reset_index(drop=True)
    df = df_small
    print("Subsampled rows:", len(df))

# features and labels
X = df.select_dtypes(include=[np.number]).drop(columns=["Label"], errors="ignore")
y = df["Label"].astype(int)

# train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
print(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")

# decide grid
auto_reduce = (args.grid == "auto")
large_threshold = 80000
use_small_grid = (args.grid == "small") or (auto_reduce and len(df) >= large_threshold)

if use_small_grid:
    param_grid = {
        "hidden_layer_sizes": [(50,), (100,)],
        "learning_rate_init": [0.001],
        "alpha": [1e-4],
        "activation": ["relu"]
    }
    print("Using SMALL grid:", param_grid)
else:
    param_grid = {
        "hidden_layer_sizes": [(50,), (100,), (100,50)],
        "learning_rate_init": [0.001, 0.01],
        "alpha": [1e-4, 1e-3],
        "activation": ["relu", "tanh"]
    }
    print("Using FULL grid:", param_grid)

mlp = MLPClassifier(max_iter=args.max_iter, early_stopping=True, random_state=42)

cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
gs = GridSearchCV(mlp, param_grid, scoring="f1", cv=cv, n_jobs=args.n_jobs, verbose=args.verbose)

print("Starting GridSearchCV for MLP...")
t0 = time.time()
try:
    gs.fit(X_train, y_train)
except KeyboardInterrupt:
    print("Interrupted by user. Exiting early.")
    raise
train_time = time.time() - t0
best = gs.best_estimator_

print("Best params:", gs.best_params_)
print(f"Grid / training time: {train_time:.2f}s")

# Evaluate
t0 = time.time()
y_pred = best.predict(X_test)
infer_time = time.time() - t0
try:
    y_prob = best.predict_proba(X_test)[:, 1]
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
    "best_params": gs.best_params_,
    "accuracy": float(acc),
    "precision": float(prec),
    "recall": float(rec),
    "f1": float(f1),
    "roc_auc": roc,
    "confusion_matrix": cm,
    "report": report,
    "train_time_seconds": train_time,
    "inference_time_seconds": infer_time,
    "sample_size_used": len(df)
}

# save outputs
joblib.dump({"model": best, "feature_columns": X.columns.tolist()}, MODEL_OUT)
with open(METRICS_OUT, "w", encoding="utf-8") as fh:
    json.dump(metrics, fh, indent=2)

# write markdown
os.makedirs(os.path.dirname(MD_OUT), exist_ok=True)
with open(MD_OUT, "w", encoding="utf-8") as fh:
    fh.write("# Day 25 — MLP (Neural Network) Results\n\n")
    fh.write(f"Model saved: `{os.path.relpath(MODEL_OUT, ROOT)}`\n\n")
    fh.write("## Data used\n")
    fh.write(f"- sample_size_used: {metrics['sample_size_used']}\n\n")
    fh.write("## Best hyperparameters\n\n")
    fh.write(str(gs.best_params_) + "\n\n")
    fh.write("## Metrics (on test set)\n\n")
    fh.write(f"- Accuracy: {acc:.4f}\n")
    fh.write(f"- Precision: {prec:.4f}\n")
    fh.write(f"- Recall: {rec:.4f}\n")
    fh.write(f"- F1-score: {f1:.4f}\n")
    fh.write(f"- ROC-AUC: {roc if roc is not None else 'N/A'}\n\n")
    fh.write("Confusion matrix:\n\n")
    fh.write(str(cm) + "\n\n")
    fh.write("Notes:\n- MLP training can be sensitive to scaling; ensure features were scaled (StandardScaler) in preprocessing.\n- Early stopping is enabled.\n- For production, consider using a smaller MLP or a dedicated deep learning framework for more complex networks.\n")
print("Saved model, metrics, and report.")
print("\nDay 25 complete ✅")
