# =====================================================
# V2 OFFLINE SVM TRAINING + EVALUATION (7 FITS)
# - Same 80/20 split
# - SVM trained on subset of TRAIN pool (500k)
# - 40–100% training sizes applied to SVM pool
# - Tested on FULL frozen 20% test set
# =====================================================

import pandas as pd
import numpy as np
import json
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

# ---------------- CONFIG ----------------
DATA_FILE = "data/final/cicids2018_v2_clean_master.csv"
MODEL_DIR = "models/phase2_offline_v2"
RESULTS_FILE = "results/svm_evaluation_v2.json"

RANDOM_STATE = 42
TRAIN_SPLIT = 0.80

# SVM configuration
SVM_POOL_SIZE = 500_000   # subset from TRAIN pool
TRAIN_SIZES = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

os.makedirs("results", exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
# ---------------------------------------

print("📥 Loading dataset...")
df = pd.read_csv(DATA_FILE)

X = df.drop(columns=["Label"])
y = df["Label"].map({"BENIGN": 0, "ATTACK": 1})

# ---------------- 80/20 SPLIT ----------------
print("✂️ Performing 80/20 train-test split...")
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    train_size=TRAIN_SPLIT,
    stratify=y,
    random_state=RANDOM_STATE
)

print(f"✅ Train pool size: {len(X_train)}")
print(f"✅ Test size (frozen): {len(X_test)}")

# ---------------- CREATE SVM TRAINING POOL ----------------
print(f"📉 Creating SVM training pool of {SVM_POOL_SIZE} samples...")

svm_idx = np.random.choice(
    len(X_train),
    SVM_POOL_SIZE,
    replace=False
)

X_svm_pool = X_train.iloc[svm_idx]
y_svm_pool = y_train.iloc[svm_idx]

# ---------------- LOAD SCALER ----------------
scaler = joblib.load(f"{MODEL_DIR}/scaler_v2.pkl")

X_svm_pool_scaled = scaler.transform(X_svm_pool)
X_test_scaled = scaler.transform(X_test)

# ---------------- TRAIN & EVALUATE SVM ----------------
results = {"SVM": {}}

for frac in TRAIN_SIZES:
    subset_size = int(len(X_svm_pool_scaled) * frac)

    X_sub = X_svm_pool_scaled[:subset_size]
    y_sub = y_svm_pool.iloc[:subset_size]

    print(f"\n🚀 Training SVM with {int(frac*100)}% of SVM pool ({subset_size} samples)")

    svm_model = SVC(
        kernel="rbf",
        C=1.0,
        gamma="scale",
        probability=True,
        random_state=RANDOM_STATE
    )

    svm_model.fit(X_sub, y_sub)

    # ---- TESTING ON FULL 20% ----
    y_pred = svm_model.predict(X_test_scaled)
    y_proba = svm_model.predict_proba(X_test_scaled)[:, 1]

    results["SVM"][f"{int(frac*100)}%"] = {
        "train_samples_used": subset_size,
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1_score": round(f1_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_proba), 4)
    }

# ---------------- SAVE FINAL MODEL (100%) ----------------
joblib.dump(svm_model, f"{MODEL_DIR}/SVM_v2.pkl")

with open(RESULTS_FILE, "w") as f:
    json.dump(results, f, indent=4)

print("\n✅ SVM 40–100% TRAINING & EVALUATION COMPLETE")
print(f"📊 Results saved to: {RESULTS_FILE}")
print(f"📦 Model saved to: {MODEL_DIR}/SVM_v2.pkl")
