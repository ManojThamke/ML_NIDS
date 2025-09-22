import os, json, joblib, time, argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix, classification_report)

# optional imports (may need pip install xgboost lightgbm)
try:
    import xgboost as xgb
except Exception:
    xgb = None
try:
    import lightgbm as lgb
except Exception:
    lgb = None

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_IN = os.path.join(ROOT, "data", "preprocessed_train.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DOCS_DIR = os.path.join(ROOT, "docs", "week4")
MODEL_OUT = os.path.join(MODELS_DIR, "stacked_ensemble.pkl")
METRICS_OUT = os.path.join(MODELS_DIR, "stacked_ensemble_metrics.json")
MD_OUT = os.path.join(DOCS_DIR, "day26_stacked_ensemble.md")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument("--sample", type=int, default=100000, help="Stratified subsample size (default 100000)")
parser.add_argument("--n_jobs", type=int, default=-1, help="n_jobs for learners (default -1 uses all cores)")
parser.add_argument("--fast", action="store_true", help="Use faster/smaller model configs")
parser.add_argument("--seed", type=int, default=42, help="Random seed")
args = parser.parse_args()

print("Loading dataset:", DATA_IN)
df = pd.read_csv(DATA_IN)
if "Label" not in df.columns:
    raise SystemExit("Label column not found in preprocessed data.")

# Subsample robustly (stratified)
if args.sample is not None and args.sample > 0 and len(df) > args.sample:
    print(f"Dataset rows: {len(df)}. Subsampling to {args.sample} (stratified).")
    classes = df["Label"].unique()
    parts = []
    total = len(df)
    for cls in classes:
        cls_df = df[df["Label"] == cls]
        prop = len(cls_df) / total
        n_cls = max(1, int(round(args.sample * prop)))
        n_cls = min(n_cls, len(cls_df))
        parts.append(cls_df.sample(n=n_cls, random_state=args.seed))
    df_small = pd.concat(parts, axis=0).reset_index(drop=True)
    if len(df_small) < args.sample:
        remaining = args.sample - len(df_small)
        pool = df.drop(index=df_small.index, errors="ignore")
        if len(pool) >= remaining:
            df_small = pd.concat([df_small, pool.sample(n=remaining, random_state=args.seed)], axis=0).reset_index(drop=True)
    df = df_small
    print("Subsampled rows:", len(df))
else:
    print(f"Using full dataset (rows = {len(df)}).")

# Features & labels (numeric)
X = df.select_dtypes(include=[np.number]).drop(columns=["Label"], errors="ignore")
y = df["Label"].astype(int)

# train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=args.seed, stratify=y)
print("Train shape:", X_train.shape, "Test shape:", X_test.shape)

# model configs (safe defaults)
if args.fast:
    rf = RandomForestClassifier(n_estimators=100, max_depth=12, n_jobs=args.n_jobs, random_state=args.seed)
    lgb_clf = None
    xgb_clf = None
else:
    rf = RandomForestClassifier(n_estimators=200, max_depth=None, n_jobs=args.n_jobs, random_state=args.seed)
    # create xgboost / lightgbm instances if available, otherwise fall back to RF clones
    if xgb is not None:
        xgb_clf = xgb.XGBClassifier(n_estimators=200, use_label_encoder=False, eval_metric="logloss", n_jobs=args.n_jobs, random_state=args.seed)
    else:
        print("Warning: xgboost not installed. Skipping XGB base model.")
        xgb_clf = None
    if lgb is not None:
        lgb_clf = lgb.LGBMClassifier(n_estimators=200, n_jobs=args.n_jobs, random_state=args.seed)
    else:
        print("Warning: lightgbm not installed. Skipping LGBM base model.")
        lgb_clf = None

# Build list of estimators — include only available models
estimators = [("rf", rf)]
if xgb_clf is not None:
    estimators.append(("xgb", xgb_clf))
if lgb_clf is not None:
    estimators.append(("lgb", lgb_clf))

print("Base estimators:", [n for n,_ in estimators])

# Meta learner
meta = LogisticRegression(max_iter=2000, solver="lbfgs", n_jobs=args.n_jobs, random_state=args.seed)

# Stacking classifier
stack = StackingClassifier(estimators=estimators, final_estimator=meta, cv=5, n_jobs=args.n_jobs, passthrough=False)

# Fit
t0 = time.time()
print("Training stacked ensemble (this may take a while depending on sample size)...")
stack.fit(X_train, y_train)
train_time = time.time() - t0
print(f"Training time: {train_time:.2f}s")

# Evaluate
t0 = time.time()
y_pred = stack.predict(X_test)
infer_time = time.time() - t0
try:
    y_prob = stack.predict_proba(X_test)[:,1]
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
    "inference_time_seconds": infer_time,
    "sample_size_used": len(df),
    "base_estimators": [name for name,_ in estimators]
}

# save
joblib.dump({"model": stack, "feature_columns": X.columns.tolist()}, MODEL_OUT)
with open(METRICS_OUT, "w", encoding="utf-8") as fh:
    json.dump(metrics, fh, indent=2)

# report markdown
with open(MD_OUT, "w", encoding="utf-8") as fh:
    fh.write("# Day 26 — Stacked Ensemble Results\n\n")
    fh.write(f"Model saved: `{os.path.relpath(MODEL_OUT, ROOT)}`\n\n")
    fh.write(f"Sample used: {len(df)} rows\n\n")
    fh.write("Base estimators:\n\n")
    for n,_ in estimators:
        fh.write(f"- {n}\n")
    fh.write("\n## Metrics (test set)\n\n")
    fh.write(f"- Accuracy: {acc:.4f}\n")
    fh.write(f"- Precision: {prec:.4f}\n")
    fh.write(f"- Recall: {rec:.4f}\n")
    fh.write(f"- F1-score: {f1:.4f}\n")
    fh.write(f"- ROC-AUC: {roc if roc is not None else 'N/A'}\n\n")
    fh.write("Confusion matrix:\n\n")
    fh.write(str(cm) + "\n\n")
    fh.write("Notes:\n- Stacking combines strengths of base learners. Training time = sum of base learners (with CV) + meta training.\n- If XGBoost/LGBM missing, script falls back to available learners.\n- For production, consider saving individual best-performing base models and using a lighter meta model.\n")
print("Saved stacked ensemble model, metrics, and report.")
print("\nDay 26 complete ✅")
