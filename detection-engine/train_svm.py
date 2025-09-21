# detection-engine/train_svm.py
"""
Day 22 — Train SVM (RBF) with safer defaults + CLI control (FULL fixed)
- Repaired Grid combos calculation (no pandas.core.* usage).
- Uses explicit per-class stratified sampling (no groupby.apply warning).
CLI:
  --sample N      : stratified subsample size (int). If omitted, uses full data (not recommended).
  --n_jobs N      : number of parallel jobs for GridSearchCV (default 1).
  --approx        : use RBFSampler + LinearSVC (approx RBF, much faster).
  --grid {small,full,auto} : choose grid size. 'auto' reduces to small for large sample sizes.
  --verbose N     : GridSearchCV verbose level (default 1)
Outputs:
  - detection-engine/models/svm.pkl
  - detection-engine/models/svm_metrics.json
  - docs/week4/day22_svm.md
"""
import os
import json
import joblib
import time
import argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.svm import SVC, LinearSVC
from sklearn.kernel_approximation import RBFSampler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix, classification_report)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_IN = os.path.join(ROOT, "data", "preprocessed_train.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DOCS_DIR = os.path.join(ROOT, "docs", "week4")
MODEL_OUT = os.path.join(MODELS_DIR, "svm.pkl")
METRICS_OUT = os.path.join(MODELS_DIR, "svm_metrics.json")
MD_OUT = os.path.join(DOCS_DIR, "day22_svm.md")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# ---- CLI ----
parser = argparse.ArgumentParser()
parser.add_argument("--sample", type=int, default=None,
                    help="Stratified subsample size (e.g. 50000 or 100000). Default: None (full) — not recommended.")
parser.add_argument("--n_jobs", type=int, default=1, help="n_jobs for GridSearchCV (default 1)")
parser.add_argument("--approx", action="store_true", help="Use RBFSampler + LinearSVC (approx RBF, much faster)")
parser.add_argument("--grid", choices=["small", "full", "auto"], default="auto",
                    help="Choose grid size. 'auto' reduces to small for large sample sizes.")
parser.add_argument("--verbose", type=int, default=1, help="GridSearchCV verbose level")
args = parser.parse_args()

print("Loading dataset:", DATA_IN)
df = pd.read_csv(DATA_IN)
if "Label" not in df.columns:
    raise SystemExit("Label column not found in preprocessed data.")

# Stratified subsample using explicit per-class sampling (avoids groupby.apply warnings)
if args.sample is not None and len(df) > args.sample:
    print(f"Dataset rows: {len(df)}. Subsampling to {args.sample} (stratified).")
    classes = df["Label"].unique()
    sampled_parts = []
    # compute desired per-class counts proportional to their frequency
    total = len(df)
    for cls in classes:
        cls_df = df[df["Label"] == cls]
        prop = len(cls_df) / total
        n_cls = max(1, int(round(args.sample * prop)))
        # ensure we don't sample more than available
        n_cls = min(n_cls, len(cls_df))
        sampled = cls_df.sample(n=n_cls, random_state=42)
        sampled_parts.append(sampled)
    df_small = pd.concat(sampled_parts, axis=0).reset_index(drop=True)
    # if undershot due to rounding or small classes, top-up random sample to reach exact size
    if len(df_small) < args.sample:
        remaining = args.sample - len(df_small)
        # take from whole df excluding already sampled indices
        remaining_pool = df.drop(index=df_small.index, errors="ignore")
        if len(remaining_pool) >= remaining:
            topup = remaining_pool.sample(n=remaining, random_state=42)
            df_small = pd.concat([df_small, topup], axis=0).reset_index(drop=True)
    df = df_small
else:
    print("Using full dataset (rows = {}).".format(len(df)))

X = df.drop(columns=["Label"])
y = df["Label"].astype(int)

# train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Decide grid based on args and sample size
auto_reduce = (args.grid == "auto")
large_sample_threshold = 70000  # if sample >= this, prefer small grid
use_small_grid = (args.grid == "small") or (auto_reduce and len(df) >= large_sample_threshold)

if args.approx:
    print("Using RBFSampler + LinearSVC (approximate RBF).")
    estimator = make_pipeline(RBFSampler(random_state=42, n_components=500), LinearSVC(max_iter=20000, dual=False, random_state=42))
    if use_small_grid:
        param_grid = {"linearsvc__C": [1.0]}
    else:
        param_grid = {"rbfsampler__gamma": [0.01, 0.1], "linearsvc__C": [0.1, 1.0, 10.0]}
else:
    estimator = SVC(probability=True, random_state=42)
    if use_small_grid:
        param_grid = {"C": [1.0], "gamma": ["scale"], "kernel": ["rbf"]}
        print("Using SMALL grid for SVC (recommended for large samples):", param_grid)
    else:
        param_grid = {"C": [0.1, 1, 10], "gamma": ["scale", "auto", 0.01], "kernel": ["rbf"]}
        print("Using FULL grid for SVC:", param_grid)

# helper to count combinations safely
def param_combo_count(pg):
    sizes = [len(v) if isinstance(v, (list, tuple)) else 1 for v in pg.values()]
    prod = 1
    for s in sizes:
        prod *= s
    return prod

combo_count = param_combo_count(param_grid)

cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
gs = GridSearchCV(estimator, param_grid, scoring="f1", cv=cv, n_jobs=args.n_jobs, verbose=args.verbose)

print("Starting GridSearchCV...")
print(f"Total samples used: {len(df)}. Grid combos: {combo_count}  (folds=3 -> total fits = {combo_count * 3})")

t0 = time.time()
try:
    gs.fit(X_train, y_train)
except KeyboardInterrupt:
    print("Interrupted by user (KeyboardInterrupt). Exiting early.")
    raise
train_time = time.time() - t0
best = gs.best_estimator_

print("Best params:", gs.best_params_)
print(f"Grid search time: {train_time:.2f}s")

# evaluate
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
    "sample_size_used": len(df),
    "grid_used": "small" if use_small_grid else "full",
    "approx_used": bool(args.approx)
}

# save model bundle (model + feature_columns)
joblib.dump({"model": best, "feature_columns": X.columns.tolist()}, MODEL_OUT)
with open(METRICS_OUT, "w", encoding="utf-8") as fh:
    json.dump(metrics, fh, indent=2)

# write docs summary
os.makedirs(os.path.dirname(MD_OUT), exist_ok=True)
with open(MD_OUT, "w", encoding="utf-8") as fh:
    fh.write("# Day 22 — SVM (RBF) Results\n\n")
    fh.write(f"Model saved: `{os.path.relpath(MODEL_OUT, ROOT)}`\n\n")
    fh.write("## Data used\n")
    fh.write(f"- sample_size_used: {metrics['sample_size_used']}\n")
    fh.write(f"- grid_used: {metrics['grid_used']}\n")
    fh.write(f"- approx_used: {metrics['approx_used']}\n\n")
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
    fh.write("Notes:\n- Kernel: RBF (or approximated if --approx). Tuned C and gamma on selected grid.\n- SVMs can be slow on large datasets; for reproducibility we used stratified subsampling when requested.\n")
print("Saved model, metrics, and report.")
print("\nDay 22 complete ✅")
