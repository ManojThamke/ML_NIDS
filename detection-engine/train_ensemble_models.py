import os, json, joblib, time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_IN = os.path.join(ROOT, "data", "preprocessed_train.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DOCS_DIR = os.path.join(ROOT, "docs")
METRICS_JSON = os.path.join(MODELS_DIR, "ensemble_metrics.json")
MODEL_RF_PATH = os.path.join(MODELS_DIR, "randomforest_ensemble.pkl")
MODEL_GBM_PATH = os.path.join(MODELS_DIR, "gbm_ensemble.pkl")
PLOT_PATH = os.path.join(DOCS_DIR, "ensemble_comparison.png")
MD_PATH = os.path.join(DOCS_DIR, "model_results.md")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

print("Loading preprocessed data:", DATA_IN)
df = pd.read_csv(DATA_IN)
if "Label" not in df.columns:
    raise SystemExit("Label column not found in preprocessed data.")

X = df.drop(columns=["Label"])
y = df["Label"].astype(int)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

models = {
    "RandomForest": RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42),
    "GBM": GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, random_state=42)
}

results = {}

for name, model in models.items():
    print(f"\nTraining {name} ...")
    t0 = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - t0

    t0 = time.time()
    y_pred = model.predict(X_test)
    infer_time = time.time() - t0

    # probability for ROC
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None

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
        "report": report,
        "train_time_seconds": train_time,
        "inference_time_seconds": infer_time
    }

    # Save model bundle (includes feature columns)
    model_path = MODEL_RF_PATH if name == "RandomForest" else MODEL_GBM_PATH
    joblib.dump({"model": model, "feature_columns": X.columns.tolist()}, model_path)
    print(f"Saved {name} to: {model_path}")
    print(f"Train time: {train_time:.2f}s  Inference time (test set): {infer_time:.4f}s")

# Persist metrics
with open(METRICS_JSON, "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=2)
print("Saved ensemble metrics to:", METRICS_JSON)

# Update docs/model_results.md (append ensemble results summary)
with open(MD_PATH, "a", encoding="utf-8") as fh:
    fh.write("\n\n# Ensemble Models — Day 18\n\n")
    fh.write("Trained models: RandomForest, GradientBoosting (sklearn)\n\n")
    for name, stats in results.items():
        fh.write(f"## {name}\n\n")
        fh.write(f"- Accuracy: {stats['accuracy']:.4f}\n")
        fh.write(f"- Precision: {stats['precision']:.4f}\n")
        fh.write(f"- Recall: {stats['recall']:.4f}\n")
        fh.write(f"- F1-score: {stats['f1']:.4f}\n")
        fh.write(f"- ROC-AUC: {stats['roc_auc'] if stats['roc_auc'] is not None else 'N/A'}\n")
        fh.write(f"- Train time (s): {stats.get('train_time_seconds', 'N/A'):.2f}\n")
        fh.write(f"- Inference time (s): {stats.get('inference_time_seconds', 'N/A'):.4f}\n\n")
        fh.write("Confusion matrix:\n\n")
        fh.write(str(stats["confusion_matrix"]) + "\n\n")
        fh.write("Short notes (speed vs accuracy):\n\n")
        fh.write("- RandomForest: typically slower to train, fast-ish inference with many trees; good accuracy and robustness.\n")
        fh.write("- GBM: often higher accuracy per-tree, slower training; inference comparable to RF depending on tree count.\n\n")
    fh.write("---\n")
print("Appended ensemble summary to:", MD_PATH)

# Plot comparison (Accuracy and F1, and train_time)
metrics_for_plot = ["accuracy", "f1"]
labels = list(results.keys())
accs = [results[k]["accuracy"] for k in labels]
f1s = [results[k]["f1"] for k in labels]
train_times = [results[k]["train_time_seconds"] for k in labels]

x = np.arange(len(labels))
width = 0.3

fig, ax1 = plt.subplots(figsize=(8,5))

ax1.bar(x - width/2, accs, width, label="Accuracy")
ax1.bar(x + width/2, f1s, width, label="F1")
ax1.set_xticks(x)
ax1.set_xticklabels(labels)
ax1.set_ylim(0,1.05)
ax1.set_ylabel("Score")
ax1.legend(loc="upper left")

# secondary axis for training time
ax2 = ax1.twinx()
ax2.plot(x, train_times, color="black", marker="o", linestyle="--", label="Train time (s)")
ax2.set_ylabel("Train time (s)")
ax2.legend(loc="upper right")

plt.title("Ensemble models comparison (Day 18)")
plt.tight_layout()
plt.savefig(PLOT_PATH)
plt.close()
print("Saved ensemble comparison plot to:", PLOT_PATH)

print("\nDay 18 complete ✅")
