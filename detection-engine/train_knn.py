import os, json, joblib, time, argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_IN = os.path.join(ROOT, "data", "preprocessed_train.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DOCS_DIR = os.path.join(ROOT, "docs", "week4")
MODEL_OUT = os.path.join(MODELS_DIR, "knn.pkl")
METRICS_OUT = os.path.join(MODELS_DIR, "knn_metrics.json")
MD_OUT = os.path.join(DOCS_DIR, "day23_knn.md")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument("--sample", type=int, default=50000, help="Stratified subsample size (default 50000)")
parser.add_argument("--ks", type=int, nargs="+", default=[3,5,7], help="k values to try (default 3 5 7)")
parser.add_argument("--n_jobs", type=int, default=-1, help="n_jobs for neighbor search (default -1)")
parser.add_argument("--metric", type=str, default="minkowski", help="distance metric (default minkowski)")
parser.add_argument("--test_ratio", type=float, default=0.25, help="test split ratio (default 0.25)")
args = parser.parse_args()

print("Loading dataset:", DATA_IN)
df = pd.read_csv(DATA_IN)
if "Label" not in df.columns:
    raise SystemExit("Label column not found in preprocessed data.")

# Subsample (stratified) if large
sample_size = args.sample
if len(df) > sample_size:
    print(f"Dataset rows: {len(df)}. Subsampling to {sample_size} (stratified).")
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
    if len(df_small) < sample_size:
        remaining = sample_size - len(df_small)
        pool = df.drop(index=df_small.index, errors="ignore")
        if len(pool) >= remaining:
            df_small = pd.concat([df_small, pool.sample(n=remaining, random_state=42)], axis=0).reset_index(drop=True)
    df = df_small
    print("Subsampled rows:", len(df))
else:
    print("Using full dataset (rows = {}).".format(len(df)))

# Use numeric features only (if preprocessed produced non-numeric, adjust earlier pipeline)
X = df.select_dtypes(include=[np.number]).drop(columns=["Label"], errors="ignore")
y = df["Label"].astype(int)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=args.test_ratio, random_state=42, stratify=y)

print(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")

best_score = -1.0
best_entry = None
results = {}

for k in args.ks:
    print(f"\nTraining KNN k={k} (n_jobs={args.n_jobs}, metric={args.metric})")
    knn = KNeighborsClassifier(n_neighbors=k, n_jobs=args.n_jobs, metric=args.metric)
    t0 = time.time()
    knn.fit(X_train, y_train)   # training stores dataset; fast
    train_time = time.time() - t0

    # Measure inference time: predict on test in batches to avoid memory spikes
    n_samples = len(X_test)
    batch = 1024
    t_pred0 = time.time()
    y_pred = knn.predict(X_test)
    t_pred1 = time.time()
    pred_time_total = t_pred1 - t_pred0
    avg_pred_ms = (pred_time_total / n_samples) * 1000.0

    # Also measure predict_proba time if available (KNN has it)
    try:
        tpp0 = time.time()
        y_prob = knn.predict_proba(X_test)[:,1]
        tpp1 = time.time()
        prob_time_total = tpp1 - tpp0
        avg_prob_ms = (prob_time_total / n_samples) * 1000.0
    except Exception:
        y_prob = None
        avg_prob_ms = None

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc = float(roc_auc_score(y_test, y_prob)) if y_prob is not None else None
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, output_dict=True)

    metrics = {
        "k": k,
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "roc_auc": roc,
        "confusion_matrix": cm,
        "report": report,
        "train_time_seconds": train_time,
        "predict_time_seconds": pred_time_total,
        "avg_predict_ms_per_sample": avg_pred_ms,
        "avg_predict_proba_ms_per_sample": avg_prob_ms,
        "n_train_samples": len(X_train),
        "n_test_samples": len(X_test)
    }

    results[f"k_{k}"] = metrics
    print(f"k={k} metrics: acc={acc:.4f} f1={f1:.4f} avg_pred_ms={avg_pred_ms:.4f}")

    if f1 > best_score:
        best_score = f1
        best_entry = (k, knn, metrics)

# Save best model bundle (note: KNN stores data; model size ~ training data)
if best_entry is not None:
    best_k, best_model, best_metrics = best_entry
    joblib.dump({"model": best_model, "feature_columns": X.columns.tolist()}, MODEL_OUT)
    with open(METRICS_OUT, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
    # write md report
    os.makedirs(os.path.dirname(MD_OUT), exist_ok=True)
    with open(MD_OUT, "w", encoding="utf-8") as fh:
        fh.write("# Day 23 — K-Nearest Neighbors (KNN) Results\n\n")
        fh.write(f"Sample used: {len(df)} rows\n\n")
        fh.write("## Tried ks\n\n")
        fh.write(", ".join(str(k) for k in args.ks) + "\n\n")
        fh.write("## Best (by F1)\n\n")
        fh.write(f"- k = {best_k}\n")
        fh.write(json.dumps(best_metrics, indent=2))
        fh.write("\n\n## All results\n\n")
        fh.write(json.dumps(results, indent=2))
        fh.write("\n\nNotes:\n- KNN stores the full training set in the model; model size ~ memory to keep training set.\n- Inference cost grows with training size; consider approximate nearest neighbor libraries (FAISS, Annoy) or KDTree for speed.\n- For realtime detection, KNN may be too slow on large training sets.\n")
    print("Saved best model and metrics.")
else:
    print("No models trained.")
