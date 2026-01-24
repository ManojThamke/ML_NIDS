import os
import json
import joblib
import time
import pandas as pd

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

# =====================================================
# PATH CONFIGURATION (EXPLICIT & SAFE)
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR, "..", "data", "final", "cicids2017_final_scaled.csv"
)

METRICS_DIR = os.path.join(BASE_DIR, "..", "docs", "metrics")
MODELS_DIR = os.path.join(BASE_DIR, "..", "models", "phase1")

os.makedirs(METRICS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

print(f"📄 Using dataset: {DATA_PATH}")

# =====================================================
# CONFIGURATION
# =====================================================
TRAIN_SIZES = [0.4, 0.5, 0.6, 0.7]
MODEL_NAME = "SupportVectorMachine"
SUBSET_SIZE = 150_000        # You may increase to 200_000 if needed
LABEL_COL = "Label"

# =====================================================
# LOAD DATASET
# =====================================================
print("📂 Loading full dataset...")
df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)

if LABEL_COL not in df.columns:
    raise ValueError("❌ 'Label' column not found in dataset")

X = df.drop(columns=[LABEL_COL])
y = df[LABEL_COL]

# =====================================================
# CREATE STRATIFIED SUBSET
# =====================================================
print(f"🔽 Creating stratified subset of {SUBSET_SIZE} samples...")

X_sub, _, y_sub, _ = train_test_split(
    X,
    y,
    train_size=SUBSET_SIZE,
    stratify=y,
    random_state=42
)

print("✅ Subset ready")
print("Subset shape:", X_sub.shape)

# =====================================================
# TRAINING LOOP
# =====================================================
for train_size in TRAIN_SIZES:
    train_pct = int(train_size * 100)
    print(f"\n🚀 Training SVM (Train {train_pct}%)")

    start_time = time.time()

    X_train, X_test, y_train, y_test = train_test_split(
        X_sub,
        y_sub,
        train_size=train_size,
        stratify=y_sub,
        random_state=42
    )

    model = SVC(
        kernel="rbf",
        C=1.0,
        gamma="scale",
        probability=True,
        class_weight="balanced",
        cache_size=4096,
        verbose=True
    )

    model.fit(X_train, y_train)

    # =================================================
    # SAVE MODEL
    # =================================================
    model_path = os.path.join(
        MODELS_DIR,
        f"svm_train{train_pct}.pkl"
    )
    joblib.dump(model, model_path)

    # =================================================
    # EVALUATION
    # =================================================
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "model": MODEL_NAME,
        "kernel": "rbf",
        "subset_size": SUBSET_SIZE,
        "train_percentage": train_pct,
        "test_percentage": 100 - train_pct,
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_prob),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "training_time_seconds": round(time.time() - start_time, 2),
        "model_path": model_path
    }

    metrics_path = os.path.join(
        METRICS_DIR,
        f"svm_train{train_pct}.json"
    )

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    print(f"✅ Model saved: {model_path}")
    print(f"✅ Metrics saved: {metrics_path}")

print("\n🎉 SVM TRAINING COMPLETED FOR ALL SPLITS")
